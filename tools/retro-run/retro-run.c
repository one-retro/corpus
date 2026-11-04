// retro-run -- play a libretro core from a script and keep the saves it writes.
//
// A descendant of cloud/tools/snes-harness. That tool answers "does a parser
// agree with the game?"; this one answers "what does this core write when a
// game saves?". So on top of the harness it behaves like RetroArch where saves
// are concerned:
//
//   * the core is given a save directory, and anything it writes there itself
//     (Beetle Saturn's .bkr, Flycast's VMUs, PPSSPP's SAVEDATA) is kept;
//   * on close, battery RAM is written to <savedir>/<stem>.srm and the clock
//     region to <stem>.rtc, before the game is unloaded, as RetroArch does;
//   * core options are answered with their defaults unless overridden.
//
// It also offers an offscreen OpenGL context (CGL on macOS) for cores that
// only render through the GPU, analog sticks, a keyboard, and save states so
// that a long script can be developed one stretch at a time.
//
//   make
//   ./retro-run --core snes9x_libretro.dylib --rom game.sfc \
//               --savedir out/ --sysdir bios/ --script run.txt --shots shots/

#define _DARWIN_C_SOURCE
#include <dlfcn.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>
#include <zlib.h>

#ifdef __APPLE__
#define GL_SILENCE_DEPRECATION
#include <OpenGL/OpenGL.h>
#include <OpenGL/gl3.h>
#define HAVE_CGL 1
#endif

// --- libretro, only the parts used here ---------------------------------

struct retro_game_info {
    const char *path;
    const void *data;
    size_t size;
    const char *meta;
};
struct retro_subsystem_memory_info { const char *extension; unsigned type; };
struct retro_subsystem_rom_info {
    const char *desc, *valid_extensions;
    bool need_fullpath, block_extract, required;
    const struct retro_subsystem_memory_info *memory;
    unsigned num_memory;
};
struct retro_subsystem_info {
    const char *desc, *ident;
    const struct retro_subsystem_rom_info *roms;
    unsigned num_roms, id;
};
#define MAX_SUBSYS 16
#define MAX_SLOTS 8
static struct retro_subsystem_info subsys[MAX_SUBSYS];
static struct retro_subsystem_rom_info subsys_roms[MAX_SUBSYS][MAX_SLOTS];
static unsigned n_subsys = 0;
static const struct retro_subsystem_info *subsys_used = NULL;
static const char *slot_paths[MAX_SLOTS];
static unsigned n_slots = 0;
static unsigned subsys_id_override = 0;
static void keep_subsystems(const struct retro_subsystem_info *s) {
    n_subsys = 0;
    for (; s && s->ident && n_subsys < MAX_SUBSYS; s++, n_subsys++) {
        subsys[n_subsys] = *s;
        subsys[n_subsys].desc = s->desc ? strdup(s->desc) : NULL;
        subsys[n_subsys].ident = strdup(s->ident);
        for (unsigned r = 0; r < s->num_roms && r < MAX_SLOTS; r++) {
            subsys_roms[n_subsys][r] = s->roms[r];
            struct retro_subsystem_memory_info *m = calloc(s->roms[r].num_memory + 1, sizeof *m);
            for (unsigned j = 0; j < s->roms[r].num_memory; j++) {
                m[j].type = s->roms[r].memory[j].type;
                m[j].extension = strdup(s->roms[r].memory[j].extension);
            }
            subsys_roms[n_subsys][r].memory = m;
            subsys_roms[n_subsys][r].desc = s->roms[r].desc ? strdup(s->roms[r].desc) : "";
        }
        subsys[n_subsys].roms = subsys_roms[n_subsys];
    }
}
struct retro_system_info {
    const char *library_name, *library_version, *valid_extensions;
    bool need_fullpath, block_extract;
};
struct retro_game_geometry {
    unsigned base_width, base_height, max_width, max_height;
    float aspect_ratio;
};
struct retro_system_timing {
    double fps, sample_rate;
};
struct retro_system_av_info {
    struct retro_game_geometry geometry;
    struct retro_system_timing timing;
};
struct retro_variable {
    const char *key, *value;
};
struct retro_log_callback {
    void (*log)(int, const char *, ...);
};
struct retro_message {
    const char *msg;
    unsigned frames;
};
struct retro_message_ext {
    const char *msg;
    unsigned duration, priority;
    int level, target, type;
    int8_t progress;
};
typedef void (*retro_proc_address_t)(void);
struct retro_hw_render_callback {
    unsigned context_type;
    void (*context_reset)(void);
    uintptr_t (*get_current_framebuffer)(void);
    retro_proc_address_t (*get_proc_address)(const char *);
    bool depth, stencil, bottom_left_origin;
    unsigned version_major, version_minor;
    bool cache_context;
    void (*context_destroy)(void);
    bool debug_context;
};
struct retro_frame_time_callback {
    void (*callback)(int64_t usec);
    int64_t reference;
};
struct retro_audio_callback {
    void (*callback)(void);
    void (*set_state)(bool);
};
struct retro_core_option_value {
    const char *value, *label;
};
#define NUM_OPTION_VALUES 128
struct retro_core_option_definition {
    const char *key, *desc, *info;
    struct retro_core_option_value values[NUM_OPTION_VALUES];
    const char *default_value;
};
struct retro_core_options_intl {
    struct retro_core_option_definition *us, *local;
};
struct retro_core_option_v2_definition {
    const char *key, *desc, *desc_categorized, *info, *info_categorized, *category_key;
    struct retro_core_option_value values[NUM_OPTION_VALUES];
    const char *default_value;
};
struct retro_core_options_v2 {
    void *categories;
    struct retro_core_option_v2_definition *definitions;
};
struct retro_core_options_v2_intl {
    struct retro_core_options_v2 *us, *local;
};
struct retro_disk_control_callback {
    bool (*set_eject_state)(bool);
    bool (*get_eject_state)(void);
    unsigned (*get_image_index)(void);
    bool (*set_image_index)(unsigned);
    unsigned (*get_num_images)(void);
    void *replace_image_index, *add_image_index;
};
struct retro_keyboard_callback {
    void (*callback)(bool down, unsigned keycode, uint32_t character, uint16_t mods);
};

#define EXPERIMENTAL 0x10000
#define ENV_SET_ROTATION 1
#define ENV_GET_OVERSCAN 2
#define ENV_GET_CAN_DUPE 3
#define ENV_SET_MESSAGE 6
#define ENV_SHUTDOWN 7
#define ENV_SET_PERFORMANCE_LEVEL 8
#define ENV_GET_SYSTEM_DIRECTORY 9
#define ENV_SET_PIXEL_FORMAT 10
#define ENV_SET_INPUT_DESCRIPTORS 11
#define ENV_SET_KEYBOARD_CALLBACK 12
#define ENV_SET_DISK_CONTROL_INTERFACE 13
#define ENV_SET_HW_RENDER 14
#define ENV_GET_VARIABLE 15
#define ENV_SET_VARIABLES 16
#define ENV_GET_VARIABLE_UPDATE 17
#define ENV_SET_SUPPORT_NO_GAME 18
#define ENV_GET_LIBRETRO_PATH 19
#define ENV_SET_FRAME_TIME_CALLBACK 21
#define ENV_SET_AUDIO_CALLBACK 22
#define ENV_GET_INPUT_DEVICE_CAPABILITIES 24
#define ENV_GET_LOG_INTERFACE 27
#define ENV_GET_CORE_ASSETS_DIRECTORY 30
#define ENV_GET_SAVE_DIRECTORY 31
#define ENV_SET_SYSTEM_AV_INFO 32
#define ENV_SET_SUBSYSTEM_INFO 34
#define ENV_SET_CONTROLLER_INFO 35
#define ENV_SET_MEMORY_MAPS 36
#define ENV_SET_GEOMETRY 37
#define ENV_GET_USERNAME 38
#define ENV_GET_LANGUAGE 39
#define ENV_SET_SUPPORT_ACHIEVEMENTS 42
#define ENV_SET_SERIALIZATION_QUIRKS 44
#define ENV_GET_AUDIO_VIDEO_ENABLE 47
#define ENV_GET_FASTFORWARDING 49
#define ENV_GET_INPUT_BITMASKS 51
#define ENV_GET_CORE_OPTIONS_VERSION 52
#define ENV_SET_CORE_OPTIONS 53
#define ENV_SET_CORE_OPTIONS_INTL 54
#define ENV_SET_CORE_OPTIONS_DISPLAY 55
#define ENV_SET_CORE_OPTIONS_V2 67
#define ENV_SET_CORE_OPTIONS_V2_INTL 68
#define ENV_SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK 69
#define ENV_GET_PREFERRED_HW_RENDER 56
#define ENV_GET_DISK_CONTROL_INTERFACE_VERSION 57
#define ENV_SET_DISK_CONTROL_EXT_INTERFACE 58
#define ENV_GET_MESSAGE_INTERFACE_VERSION 59
#define ENV_SET_MESSAGE_EXT 60
#define ENV_GET_INPUT_MAX_USERS 61
#define ENV_SET_CONTENT_INFO_OVERRIDE 65
#define ENV_SET_VARIABLE 70
#define ENV_GET_THROTTLE_STATE 71
#define ENV_GET_JIT_CAPABLE 74

#define MEM_SAVE_RAM 0
#define MEM_RTC 1
#define MEM_SYSTEM_RAM 2
#define DEV_JOYPAD 1
#define DEV_KEYBOARD 3
#define DEV_ANALOG 5
#define DEV_POINTER 6
#define DEV_MOUSE 2
#define JOYPAD_MASK 256

#define HW_NONE 0
#define HW_OPENGL 1
#define HW_OPENGLES2 2
#define HW_OPENGL_CORE 3
#define HW_OPENGLES3 4
#define HW_OPENGLES_VERSION 5
#define HW_FRAME_VALID ((const void *)-1)

#define FMT_0RGB1555 0
#define FMT_XRGB8888 1
#define FMT_RGB565 2

/// Joypad buttons, in libretro's id order. These are the names a script uses.
static const char *BTN[] = {"b",  "y", "select", "start", "up", "down", "left", "right",
                            "a",  "x", "l",      "r",     "l2", "r2",   "l3",   "r3"};
#define NBTN 16

/// Keys a script can type, with their libretro keycodes (RETROK_*), which are
/// SDL 1.2's. Letters and digits are their ASCII codes and are handled apart.
static const struct {
    const char *name;
    unsigned code;
} KEYS[] = {
    {"backspace", 8}, {"tab", 9},     {"return", 13},  {"enter", 13},   {"escape", 27},
    {"space", 32},    {"comma", 44},  {"minus", 45},   {"period", 46},  {"slash", 47},
    {"semicolon", 59}, {"equals", 61}, {"delete", 127}, {"up", 273},     {"down", 274},
    {"right", 275},   {"left", 276},  {"insert", 277}, {"home", 278},   {"end", 279},
    {"pageup", 280},  {"pagedown", 281}, {"f1", 282},  {"f2", 283},     {"f3", 284},
    {"f4", 285},      {"f5", 286},    {"f6", 287},     {"f7", 288},     {"f8", 289},
    {"f9", 290},      {"f10", 291},   {"f11", 292},    {"f12", 293},    {"rshift", 303},
    {"lshift", 304},  {"shift", 304}, {"rctrl", 305},  {"lctrl", 306},  {"ctrl", 306},
    {"ralt", 307},    {"lalt", 308},  {"alt", 308},
};
#define NKEYS (sizeof KEYS / sizeof KEYS[0])

// --- state --------------------------------------------------------------

static int pix_fmt = FMT_0RGB1555;
static void *fb = NULL;
static size_t fb_cap = 0;
static unsigned fb_w, fb_h;
static size_t fb_pitch;
static bool fb_is_hw = false;   // the last frame is in the GL framebuffer
static uint32_t held = 0;       // bitmask over BTN for port 0
static uint32_t held2 = 0;      // and for port 1
static int16_t analog[2][2][2]; // [port][stick][axis]
static bool keys_down[512];
static int16_t ptr_x, ptr_y; // pointer position, libretro's -0x7fff..0x7fff
static bool ptr_down = false;
static const char *sysdir = ".";
static const char *savedir = ".";
static const char *shots_dir = ".";
static const char *core_path = "";
static int shot_seq = 0;
static bool quiet = false;
static bool want_hw = true;
static long frame_no = 0;
static bool shutdown_requested = false;

static struct retro_frame_time_callback frame_time_cb;
static bool have_frame_time_cb = false;
static struct retro_audio_callback audio_cb;
static bool have_audio_cb = false;
static struct retro_disk_control_callback disk_cb;
static bool have_disk_cb = false;
static struct retro_keyboard_callback kb_cb;
static bool have_kb_cb = false;

// Core options: a key, the value the core will be told, and whether a user
// set it (a user's value survives the core declaring its defaults).
#define MAXOPT 1024
static struct {
    char *key, *value;
    bool user;
} opts[MAXOPT];
static int nopts = 0;

static void note(const char *fmt, ...) {
    if (quiet) return;
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
}

static int opt_find(const char *key) {
    for (int i = 0; i < nopts; i++)
        if (!strcmp(opts[i].key, key)) return i;
    return -1;
}

static void opt_set(const char *key, const char *value, bool user) {
    int i = opt_find(key);
    if (i >= 0) {
        if (opts[i].user && !user) return;
        free(opts[i].value);
        opts[i].value = strdup(value);
        opts[i].user = opts[i].user || user;
        return;
    }
    if (nopts == MAXOPT) return;
    opts[nopts].key = strdup(key);
    opts[nopts].value = strdup(value);
    opts[nopts].user = user;
    nopts++;
}

static void load_options(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) {
        perror(path);
        exit(1);
    }
    char line[1024];
    while (fgets(line, sizeof line, f)) {
        char *hash = strchr(line, '#');
        if (hash) *hash = 0;
        char *eq = strchr(line, '=');
        if (!eq) continue;
        *eq = 0;
        char *k = line, *v = eq + 1;
        while (*k == ' ' || *k == '\t') k++;
        char *ke = k + strlen(k);
        while (ke > k && (ke[-1] == ' ' || ke[-1] == '\t')) *--ke = 0;
        while (*v == ' ' || *v == '\t' || *v == '"') v++;
        char *ve = v + strlen(v);
        while (ve > v && (ve[-1] == '\n' || ve[-1] == '\r' || ve[-1] == ' ' || ve[-1] == '"'))
            *--ve = 0;
        if (*k) opt_set(k, v, true);
    }
    fclose(f);
}

// --- OpenGL, offscreen --------------------------------------------------

static struct retro_hw_render_callback hw;
static bool hw_active = false;
#ifdef HAVE_CGL
static CGLContextObj gl_ctx = NULL;
static GLuint gl_fbo = 0, gl_tex = 0, gl_rb = 0;
static unsigned gl_w = 0, gl_h = 0;
static void *gl_lib = NULL;

static uintptr_t hw_get_fb(void) { return gl_fbo; }

static retro_proc_address_t hw_get_proc(const char *sym) {
    if (!gl_lib)
        gl_lib = dlopen("/System/Library/Frameworks/OpenGL.framework/OpenGL", RTLD_LAZY);
    return (retro_proc_address_t)dlsym(gl_lib ? gl_lib : RTLD_DEFAULT, sym);
}

static bool gl_create_context(void) {
    bool core = hw.context_type == HW_OPENGL_CORE;
    CGLPixelFormatAttribute attrs[] = {
        kCGLPFAOpenGLProfile,
        (CGLPixelFormatAttribute)(core ? kCGLOGLPVersion_GL4_Core : kCGLOGLPVersion_Legacy),
        kCGLPFAColorSize, (CGLPixelFormatAttribute)24,
        kCGLPFAAlphaSize, (CGLPixelFormatAttribute)8,
        kCGLPFADepthSize, (CGLPixelFormatAttribute)24,
        kCGLPFAStencilSize, (CGLPixelFormatAttribute)8,
        kCGLPFAAccelerated,
        (CGLPixelFormatAttribute)0};
    CGLPixelFormatObj pf = NULL;
    GLint npf = 0;
    if (CGLChoosePixelFormat(attrs, &pf, &npf) != kCGLNoError || !pf) {
        fprintf(stderr, "no OpenGL pixel format for context type %u\n", hw.context_type);
        return false;
    }
    CGLError e = CGLCreateContext(pf, NULL, &gl_ctx);
    CGLDestroyPixelFormat(pf);
    if (e != kCGLNoError) {
        fprintf(stderr, "could not create an OpenGL context: %d\n", e);
        return false;
    }
    CGLSetCurrentContext(gl_ctx);
    note("  OpenGL %s on %s\n", glGetString(GL_VERSION), glGetString(GL_RENDERER));
    return true;
}

static void gl_make_fbo(unsigned w, unsigned h) {
    if (w <= gl_w && h <= gl_h && gl_fbo) return;
    if (w < gl_w) w = gl_w;
    if (h < gl_h) h = gl_h;
    if (gl_fbo) {
        glDeleteFramebuffers(1, &gl_fbo);
        glDeleteTextures(1, &gl_tex);
        glDeleteRenderbuffers(1, &gl_rb);
    }
    glGenTextures(1, &gl_tex);
    glBindTexture(GL_TEXTURE_2D, gl_tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glGenFramebuffers(1, &gl_fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, gl_fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, gl_tex, 0);
    glGenRenderbuffers(1, &gl_rb);
    glBindRenderbuffer(GL_RENDERBUFFER, gl_rb);
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, w, h);
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, gl_rb);
    GLenum st = glCheckFramebufferStatus(GL_FRAMEBUFFER);
    if (st != GL_FRAMEBUFFER_COMPLETE) fprintf(stderr, "framebuffer incomplete: 0x%x\n", st);
    glClearColor(0, 0, 0, 1);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
    gl_w = w;
    gl_h = h;
    note("  framebuffer %ux%u\n", w, h);
}

/// Copy the GL frame into `fb` as XRGB8888, top row first.
static void gl_read_frame(void) {
    size_t pitch = (size_t)fb_w * 4;
    size_t need = pitch * fb_h;
    if (need > fb_cap) {
        fb = realloc(fb, need);
        fb_cap = need;
    }
    uint8_t *tmp = malloc(need);
    glBindFramebuffer(GL_FRAMEBUFFER, gl_fbo);
    glPixelStorei(GL_PACK_ALIGNMENT, 1);
    glReadPixels(0, 0, fb_w, fb_h, GL_BGRA, GL_UNSIGNED_INT_8_8_8_8_REV, tmp);
    // libretro's default is a top-left origin: the core draws the image's top
    // row at GL's y = 0, so glReadPixels already returns it top first. Only a
    // core that asked for bottom_left_origin drew it the GL way up.
    for (unsigned y = 0; y < fb_h; y++) {
        unsigned src = hw.bottom_left_origin ? fb_h - 1 - y : y;
        memcpy((uint8_t *)fb + (size_t)y * pitch, tmp + (size_t)src * pitch, pitch);
    }
    free(tmp);
    fb_pitch = pitch;
}
#endif

static bool hw_accept(struct retro_hw_render_callback *cb) {
#ifdef HAVE_CGL
    if (!want_hw) return false;
    if (cb->context_type != HW_OPENGL && cb->context_type != HW_OPENGL_CORE) {
        note("  core asked for HW context type %u; only OpenGL is offered\n", cb->context_type);
        return false;
    }
    hw = *cb;
    if (!gl_ctx && !gl_create_context()) return false;
    cb->get_current_framebuffer = hw_get_fb;
    cb->get_proc_address = hw_get_proc;
    hw.get_current_framebuffer = hw_get_fb;
    hw.get_proc_address = hw_get_proc;
    hw_active = true;
    note("  HW render: context %u, version %u.%u, depth %d stencil %d\n", cb->context_type,
         cb->version_major, cb->version_minor, cb->depth, cb->stencil);
    return true;
#else
    (void)cb;
    return false;
#endif
}

// --- libretro callbacks -------------------------------------------------

static void env_log(int level, const char *fmt, ...) {
    if (quiet && level < 3) return;
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
}

static struct retro_system_av_info av;

/// A declared option's value is its default, or failing that its first value,
/// unless the user set it.
static void declare_option(const char *key, const char *def, const struct retro_core_option_value *values) {
    if (!key) return;
    if (!def || !*def) def = values[0].value;
    if (def) opt_set(key, def, false);
}

static void declare_v1(const struct retro_core_option_definition *d) {
    for (; d && d->key; d++) declare_option(d->key, d->default_value, d->values);
}

static void declare_v2(const struct retro_core_option_v2_definition *d) {
    for (; d && d->key; d++) declare_option(d->key, d->default_value, d->values);
}

static bool cb_env(unsigned cmd, void *data) {
    switch (cmd & ~EXPERIMENTAL) {
    case ENV_GET_CAN_DUPE:
        *(bool *)data = true;
        return true;
    case ENV_GET_OVERSCAN:
        *(bool *)data = false;
        return true;
    case ENV_SET_PIXEL_FORMAT:
        pix_fmt = *(const int *)data;
        return pix_fmt <= 2;
    case ENV_GET_SYSTEM_DIRECTORY:
    case ENV_GET_CORE_ASSETS_DIRECTORY:
        *(const char **)data = sysdir;
        return true;
    case ENV_GET_SAVE_DIRECTORY:
        *(const char **)data = savedir;
        return true;
    case ENV_GET_LIBRETRO_PATH:
        *(const char **)data = core_path;
        return true;
    case ENV_GET_LOG_INTERFACE:
        ((struct retro_log_callback *)data)->log = env_log;
        return true;
    case ENV_GET_USERNAME:
        *(const char **)data = "Player";
        return true;
    case ENV_GET_LANGUAGE:
        *(unsigned *)data = 0; // English
        return true;
    case ENV_SET_MESSAGE:
        note("  [core message] %s\n", ((const struct retro_message *)data)->msg);
        return true;
    case ENV_SET_MESSAGE_EXT:
        note("  [core message] %s\n", ((const struct retro_message_ext *)data)->msg);
        return true;
    case ENV_GET_MESSAGE_INTERFACE_VERSION:
        *(unsigned *)data = 1;
        return true;
    case ENV_SHUTDOWN:
        shutdown_requested = true;
        return true;
    case ENV_SET_SUBSYSTEM_INFO:
        keep_subsystems(data);
        return true;
    case ENV_SET_ROTATION:
    case ENV_SET_PERFORMANCE_LEVEL:
    case ENV_SET_INPUT_DESCRIPTORS:
    case ENV_SET_SUPPORT_NO_GAME:
    case ENV_SET_CONTROLLER_INFO:
    case ENV_SET_MEMORY_MAPS:
    case ENV_SET_SUPPORT_ACHIEVEMENTS:
    case ENV_SET_SERIALIZATION_QUIRKS:
    case ENV_SET_CORE_OPTIONS_DISPLAY:
    case ENV_SET_CONTENT_INFO_OVERRIDE:
        return true;
    case ENV_SET_GEOMETRY: {
        const struct retro_game_geometry *g = data;
        av.geometry.base_width = g->base_width;
        av.geometry.base_height = g->base_height;
        return true;
    }
    case ENV_SET_SYSTEM_AV_INFO:
        av = *(const struct retro_system_av_info *)data;
#ifdef HAVE_CGL
        if (hw_active && gl_fbo) gl_make_fbo(av.geometry.max_width, av.geometry.max_height);
#endif
        return true;
    case ENV_SET_DISK_CONTROL_INTERFACE:
    case ENV_SET_DISK_CONTROL_EXT_INTERFACE:
        // The extended interface begins with the same members; only those are
        // used. A core may pass NULL (Genesis Plus GX does) to withdraw it.
        if (!data) {
            have_disk_cb = false;
            return true;
        }
        memcpy(&disk_cb, data, sizeof disk_cb);
        have_disk_cb = true;
        return true;
    case ENV_GET_DISK_CONTROL_INTERFACE_VERSION:
        *(unsigned *)data = 1;
        return true;
    case ENV_SET_KEYBOARD_CALLBACK:
        kb_cb = *(const struct retro_keyboard_callback *)data;
        have_kb_cb = true;
        return true;
    case ENV_SET_FRAME_TIME_CALLBACK:
        frame_time_cb = *(const struct retro_frame_time_callback *)data;
        have_frame_time_cb = true;
        return true;
    case ENV_SET_AUDIO_CALLBACK:
        audio_cb = *(const struct retro_audio_callback *)data;
        have_audio_cb = true;
        return true;
    case ENV_GET_INPUT_DEVICE_CAPABILITIES:
        *(uint64_t *)data = (1 << DEV_JOYPAD) | (1 << DEV_ANALOG) | (1 << DEV_KEYBOARD) |
                            (1 << DEV_POINTER) | (1 << DEV_MOUSE);
        return true;
    case ENV_GET_INPUT_BITMASKS:
        return true;
    case ENV_GET_INPUT_MAX_USERS:
        *(unsigned *)data = 2;
        return true;
    case ENV_GET_AUDIO_VIDEO_ENABLE:
        *(int *)data = 3; // video and audio
        return true;
    case ENV_GET_FASTFORWARDING:
        *(bool *)data = false;
        return true;
    case ENV_GET_JIT_CAPABLE:
        *(bool *)data = true;
        return true;
    case ENV_GET_CORE_OPTIONS_VERSION:
        // Version 2, as RetroArch reports. Some cores (SkyEmu) only declare
        // their options through v2 and crash reading an option never declared.
        *(unsigned *)data = 2;
        return true;
    case ENV_SET_CORE_OPTIONS:
        declare_v1(data);
        return true;
    case ENV_SET_CORE_OPTIONS_INTL:
        declare_v1(((const struct retro_core_options_intl *)data)->us);
        return true;
    case ENV_SET_CORE_OPTIONS_V2:
        if (data) declare_v2(((const struct retro_core_options_v2 *)data)->definitions);
        return true;
    case ENV_SET_CORE_OPTIONS_V2_INTL: {
        const struct retro_core_options_v2 *us = ((const struct retro_core_options_v2_intl *)data)->us;
        if (us) declare_v2(us->definitions);
        return true;
    }
    case ENV_SET_CORE_OPTIONS_UPDATE_DISPLAY_CALLBACK:
        return true;
    case ENV_SET_VARIABLES: {
        for (const struct retro_variable *v = data; v && v->key; v++) {
            // "Description; default|other|..."
            const char *semi = strchr(v->value, ';');
            const char *p = semi ? semi + 1 : v->value;
            while (*p == ' ') p++;
            const char *bar = strchr(p, '|');
            size_t n = bar ? (size_t)(bar - p) : strlen(p);
            char def[256];
            if (n >= sizeof def) n = sizeof def - 1;
            memcpy(def, p, n);
            def[n] = 0;
            opt_set(v->key, def, false);
        }
        return true;
    }
    case ENV_SET_VARIABLE: {
        const struct retro_variable *v = data;
        if (!v) return true;
        if (v->key && v->value) opt_set(v->key, v->value, false);
        return true;
    }
    case ENV_GET_VARIABLE: {
        struct retro_variable *v = data;
        int i = opt_find(v->key);
        if (i < 0) {
            v->value = NULL;
            return false;
        }
        v->value = opts[i].value;
        return true;
    }
    case ENV_GET_VARIABLE_UPDATE:
        *(bool *)data = false;
        return true;
    case ENV_SET_HW_RENDER:
        return hw_accept(data);
    case ENV_GET_PREFERRED_HW_RENDER:
        *(unsigned *)data = want_hw ? HW_OPENGL_CORE : HW_NONE;
        return want_hw;
    default:
        return false;
    }
}

static void cb_video(const void *data, unsigned w, unsigned h, size_t pitch) {
    if (!data) return; // a duplicate of the last frame
    if (data == HW_FRAME_VALID) {
        fb_w = w;
        fb_h = h;
        fb_is_hw = true;
        return;
    }
    fb_is_hw = false;
    size_t need = pitch * h;
    if (need > fb_cap) {
        void *grown = realloc(fb, need);
        if (!grown) {
            fprintf(stderr, "out of memory for a %zu-byte frame\n", need);
            exit(1);
        }
        fb = grown;
        fb_cap = need;
    }
    memcpy(fb, data, need);
    fb_w = w;
    fb_h = h;
    fb_pitch = pitch;
}

static void cb_audio_sample(int16_t l, int16_t r) { (void)l; (void)r; }
static size_t cb_audio_batch(const int16_t *d, size_t frames) { (void)d; return frames; }
static void cb_input_poll(void) {}

static int16_t cb_input_state(unsigned port, unsigned dev, unsigned idx, unsigned id) {
    if (port > 1) return 0;
    uint32_t mask = port == 0 ? held : held2;
    switch (dev & 0xFF) {
    case DEV_JOYPAD:
        if (id == JOYPAD_MASK) return (int16_t)(mask & 0xFFFF);
        return id < NBTN ? (mask >> id) & 1 : 0;
    case DEV_ANALOG:
        if (idx < 2 && id < 2) return analog[port][idx][id];
        return 0;
    case DEV_KEYBOARD:
        return port == 0 && id < 512 ? keys_down[id] : 0;
    case DEV_POINTER:
        // A touchscreen: X, Y in -0x7fff..0x7fff across the frame, then pressed.
        if (port != 0 || idx != 0) return 0;
        if (id == 0) return ptr_x;
        if (id == 1) return ptr_y;
        if (id == 2) return ptr_down;
        return 0;
    case DEV_MOUSE:
        // Only the left button, for cores that read a touch as a click.
        if (port == 0 && id == 2) return ptr_down;
        return 0;
    default:
        return 0;
    }
}

// --- PNG ----------------------------------------------------------------

static void be32(uint8_t *p, uint32_t v) {
    p[0] = v >> 24;
    p[1] = v >> 16;
    p[2] = v >> 8;
    p[3] = v;
}

static void png_chunk(FILE *f, const char *tag, const uint8_t *buf, size_t n) {
    uint8_t len[4];
    be32(len, (uint32_t)n);
    fwrite(len, 1, 4, f);
    fwrite(tag, 1, 4, f);
    if (n) fwrite(buf, 1, n, f);
    uLong c = crc32(0, (const Bytef *)tag, 4);
    if (n) c = crc32(c, buf, (uInt)n);
    uint8_t crc[4];
    be32(crc, (uint32_t)c);
    fwrite(crc, 1, 4, f);
}

static void row_rgb(uint8_t *dst, const uint8_t *src, unsigned w, int fmt) {
    for (unsigned x = 0; x < w; x++) {
        unsigned r, g, b;
        if (fmt == FMT_XRGB8888) {
            uint32_t p = ((const uint32_t *)src)[x];
            r = (p >> 16) & 0xFF;
            g = (p >> 8) & 0xFF;
            b = p & 0xFF;
        } else {
            uint16_t p = ((const uint16_t *)src)[x];
            if (fmt == FMT_RGB565) {
                r = ((p >> 11) & 0x1F) * 255 / 31;
                g = ((p >> 5) & 0x3F) * 255 / 63;
                b = (p & 0x1F) * 255 / 31;
            } else {
                r = ((p >> 10) & 0x1F) * 255 / 31;
                g = ((p >> 5) & 0x1F) * 255 / 31;
                b = (p & 0x1F) * 255 / 31;
            }
        }
        dst[x * 3] = r;
        dst[x * 3 + 1] = g;
        dst[x * 3 + 2] = b;
    }
}

static int png_write(const char *path) {
    int fmt = pix_fmt;
#ifdef HAVE_CGL
    if (fb_is_hw && hw_active) {
        gl_read_frame();
        fmt = FMT_XRGB8888;
    }
#endif
    if (!fb || !fb_w || !fb_h) {
        fprintf(stderr, "no frame to write yet: run some frames before `shot`\n");
        return -1;
    }
    FILE *f = fopen(path, "wb");
    if (!f) {
        perror(path);
        return -1;
    }
    fwrite("\x89PNG\r\n\x1a\n", 1, 8, f);
    uint8_t ihdr[13];
    be32(ihdr, fb_w);
    be32(ihdr + 4, fb_h);
    ihdr[8] = 8;
    ihdr[9] = 2;
    ihdr[10] = ihdr[11] = ihdr[12] = 0;
    png_chunk(f, "IHDR", ihdr, sizeof ihdr);

    int rc = -1;
    size_t raw_n = (size_t)fb_h * (1 + (size_t)fb_w * 3);
    uint8_t *raw = malloc(raw_n);
    uLongf zn = compressBound(raw_n);
    uint8_t *z = malloc(zn);
    if (!raw || !z) goto done;
    uint8_t *p = raw;
    for (unsigned y = 0; y < fb_h; y++) {
        *p++ = 0;
        row_rgb(p, (const uint8_t *)fb + (size_t)y * fb_pitch, fb_w, fmt);
        p += (size_t)fb_w * 3;
    }
    if (compress2(z, &zn, raw, raw_n, 6) != Z_OK) goto done;
    png_chunk(f, "IDAT", z, zn);
    png_chunk(f, "IEND", NULL, 0);
    rc = 0;
done:
    free(raw);
    free(z);
    fclose(f);
    return rc;
}

// --- core binding -------------------------------------------------------

#define SYMS                                                                             \
    X(void, retro_init, (void))                                                          \
    X(void, retro_deinit, (void))                                                        \
    X(void, retro_set_environment, (bool (*)(unsigned, void *)))                         \
    X(void, retro_set_video_refresh, (void (*)(const void *, unsigned, unsigned, size_t)))\
    X(void, retro_set_audio_sample, (void (*)(int16_t, int16_t)))                        \
    X(void, retro_set_audio_sample_batch, (size_t (*)(const int16_t *, size_t)))         \
    X(void, retro_set_input_poll, (void (*)(void)))                                      \
    X(void, retro_set_input_state, (int16_t (*)(unsigned, unsigned, unsigned, unsigned))) \
    X(void, retro_set_controller_port_device, (unsigned, unsigned))                      \
    X(void, retro_get_system_info, (struct retro_system_info *))                         \
    X(bool, retro_load_game, (const struct retro_game_info *))                           \
    X(void, retro_unload_game, (void))                                                   \
    X(bool, retro_load_game_special, (unsigned, const struct retro_game_info *, size_t))   \
    X(void, retro_get_system_av_info, (struct retro_system_av_info *))                   \
    X(void, retro_run, (void))                                                           \
    X(void, retro_reset, (void))                                                         \
    X(size_t, retro_serialize_size, (void))                                              \
    X(bool, retro_serialize, (void *, size_t))                                           \
    X(bool, retro_unserialize, (const void *, size_t))                                   \
    X(void *, retro_get_memory_data, (unsigned))                                         \
    X(size_t, retro_get_memory_size, (unsigned))

#define X(ret, name, args) static ret(*name) args;
SYMS
#undef X

static void bind_core(const char *path) {
    void *h = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!h) {
        fprintf(stderr, "cannot open core: %s\n", dlerror());
        exit(1);
    }
#define X(ret, name, args)                                                               \
    name = (ret(*) args)dlsym(h, #name);                                                 \
    if (!name) {                                                                         \
        fprintf(stderr, "%s is missing %s: is it a libretro core?\n", path, #name);       \
        exit(1);                                                                         \
    }
    SYMS
#undef X
}

// --- running ------------------------------------------------------------

// --pace FPS: run at most FPS frames per wall-clock second. For cores whose
// emulation runs on its own thread at real-time speed and whose retro_run returns at once
// (ARMSX2 with its Null GS), so that script frames map to the emulator's frames.
static double pace_fps = 0;
static double pace_t0 = -1;
static double wall(void) { struct timeval tv; gettimeofday(&tv, NULL); return tv.tv_sec + tv.tv_usec / 1e6; }

static void pace(void) {
    if (pace_fps <= 0) return;
    if (pace_t0 < 0) pace_t0 = wall() - frame_no / pace_fps;
    double due = pace_t0 + frame_no / pace_fps, now = wall();
    if (due > now) {
        struct timespec ts = {(time_t)(due - now), (long)((due - now - (time_t)(due - now)) * 1e9)};
        nanosleep(&ts, NULL);
    }
}

static void run_frames(long n) {
    for (long i = 0; i < n && !shutdown_requested; i++) {
        pace();
        if (have_frame_time_cb) frame_time_cb.callback(frame_time_cb.reference);
        if (have_audio_cb) audio_cb.callback();
#ifdef HAVE_CGL
        if (hw_active) CGLSetCurrentContext(gl_ctx);
#endif
        retro_run();
        frame_no++;
    }
}

static uint32_t btn_mask(const char *spec, int line) {
    uint32_t mask = 0;
    char buf[128];
    snprintf(buf, sizeof buf, "%s", spec);
    for (char *tok = strtok(buf, "+"); tok; tok = strtok(NULL, "+")) {
        int found = -1;
        for (int i = 0; i < NBTN; i++)
            if (!strcmp(tok, BTN[i])) { found = i; break; }
        if (found < 0) {
            fprintf(stderr, "line %d: no such button '%s'\n", line, tok);
            exit(1);
        }
        mask |= 1u << found;
    }
    return mask;
}

static int key_code(const char *name, int line) {
    // kcN: a raw libretro keycode, for keys without a name here.
    if (name[0] == 'k' && name[1] == 'c' && name[2] >= '0' && name[2] <= '9') {
        int code = atoi(name + 2);
        if (code > 0 && code < 512) return code;
    }
    if (strlen(name) == 1) {
        char c = name[0];
        if (c >= 'A' && c <= 'Z') c = c - 'A' + 'a';
        if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9')) return c;
    }
    for (size_t i = 0; i < NKEYS; i++)
        if (!strcasecmp(name, KEYS[i].name)) return KEYS[i].code;
    fprintf(stderr, "line %d: no such key '%s'\n", line, name);
    exit(1);
}

static void key_event(int code, bool down) {
    keys_down[code] = down;
    if (have_kb_cb) {
        uint32_t ch = (code < 128) ? (uint32_t)code : 0;
        kb_cb.callback(down, code, down ? ch : 0, 0);
    }
}

static bool write_file(const char *path, const void *d, size_t n) {
    FILE *f = fopen(path, "wb");
    if (!f) {
        perror(path);
        return false;
    }
    fwrite(d, 1, n, f);
    fclose(f);
    return true;
}

static void *read_file(const char *path, size_t *n) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    void *d = malloc(len > 0 ? (size_t)len : 1);
    *n = fread(d, 1, len > 0 ? (size_t)len : 0, f);
    fclose(f);
    return d;
}

static void dump_mem(unsigned which, const char *path) {
    void *d = retro_get_memory_data(which);
    size_t n = retro_get_memory_size(which);
    if (!d || !n) {
        fprintf(stderr, "this core exposes no memory region %u\n", which);
        return;
    }
    if (write_file(path, d, n)) note("  dumped region %u -> %s (%zu bytes)\n", which, path, n);
}

static void load_mem(unsigned which, const char *path) {
    void *d = retro_get_memory_data(which);
    size_t n = retro_get_memory_size(which);
    if (!d || !n) {
        fprintf(stderr, "this core exposes no memory region %u to load %s into\n", which, path);
        return;
    }
    size_t got = 0;
    void *src = read_file(path, &got);
    if (!src) {
        perror(path);
        exit(1);
    }
    memcpy(d, src, got < n ? got : n);
    free(src);
    note("  loaded %s: %zu bytes into region %u (%zu)\n", path, got, which, n);
}

static void save_state(const char *path) {
    size_t n = retro_serialize_size();
    void *d = malloc(n ? n : 1);
    if (!n || !retro_serialize(d, n)) {
        fprintf(stderr, "the core could not save a state\n");
        free(d);
        return;
    }
    if (write_file(path, d, n)) note("  state -> %s (%zu bytes)\n", path, n);
    free(d);
}

static void load_state(const char *path) {
    size_t n = 0;
    void *d = read_file(path, &n);
    if (!d) {
        perror(path);
        exit(1);
    }
    if (!retro_unserialize(d, n)) fprintf(stderr, "the core refused state %s\n", path);
    else note("  loaded state %s\n", path);
    free(d);
}

static void do_shot(const char *name) {
    char path[2048];
    if (name && *name)
        snprintf(path, sizeof path, "%s/%s.png", shots_dir, name);
    else
        snprintf(path, sizeof path, "%s/%03d.png", shots_dir, shot_seq);
    shot_seq++;
    if (png_write(path) == 0) note("  shot -> %s (%ux%u, frame %ld)\n", path, fb_w, fb_h, frame_no);
}

static int16_t axis_value(const char *s) {
    if (!strcmp(s, "min") || !strcmp(s, "-")) return -32767;
    if (!strcmp(s, "max") || !strcmp(s, "+")) return 32767;
    if (!strcmp(s, "0") || !strcmp(s, "mid")) return 0;
    return (int16_t)atoi(s);
}

// --- script -------------------------------------------------------------

#define MAXLINES 20000
static char *lines[MAXLINES];
static int nlines = 0;

static void read_script(const char *path, int depth) {
    if (depth > 8) {
        fprintf(stderr, "include nesting too deep at %s\n", path);
        exit(1);
    }
    FILE *f = strcmp(path, "-") ? fopen(path, "r") : stdin;
    if (!f) {
        perror(path);
        exit(1);
    }
    char line[512];
    while (fgets(line, sizeof line, f)) {
        char *hash = strchr(line, '#');
        if (hash) *hash = 0;
        char cmd[64] = "", a1[400] = "";
        if (sscanf(line, "%63s %399s", cmd, a1) >= 2 && !strcmp(cmd, "include")) {
            // The rest of the line is the path, spaces and all.
            const char *rest = strstr(line, "include") + 7;
            while (*rest == ' ' || *rest == '\t') rest++;
            snprintf(a1, sizeof a1, "%s", rest);
            size_t n = strlen(a1);
            while (n && (a1[n - 1] == '\n' || a1[n - 1] == '\r' || a1[n - 1] == ' ')) a1[--n] = 0;
            // Relative to the including script.
            char inc[1024];
            if (a1[0] == '/') snprintf(inc, sizeof inc, "%s", a1);
            else {
                const char *slash = strrchr(path, '/');
                if (slash) snprintf(inc, sizeof inc, "%.*s/%s", (int)(slash - path), path, a1);
                else snprintf(inc, sizeof inc, "%s", a1);
            }
            read_script(inc, depth + 1);
            continue;
        }
        if (nlines == MAXLINES) {
            fprintf(stderr, "script too long\n");
            exit(1);
        }
        lines[nlines++] = strdup(line);
    }
    if (f != stdin) fclose(f);
}

/// Run lines [from, to). Returns the index after the block's `end` when
/// called for a repeat body.
static void run_lines(int from, int to);

static int find_end(int from) {
    int depth = 0;
    for (int i = from; i < nlines; i++) {
        char cmd[64] = "";
        if (sscanf(lines[i], "%63s", cmd) < 1) continue;
        if (!strcmp(cmd, "repeat")) depth++;
        else if (!strcmp(cmd, "end")) {
            if (depth == 0) return i;
            depth--;
        }
    }
    fprintf(stderr, "repeat without end\n");
    exit(1);
}

static void run_lines(int from, int to) {
    for (int i = from; i < to && !shutdown_requested; i++) {
        int lineno = i + 1;
        char cmd[64] = "", a1[400] = "", a2[64] = "", a3[64] = "";
        if (sscanf(lines[i], "%63s %399s %63s %63s", cmd, a1, a2, a3) < 1) continue;

        if (!strcmp(cmd, "wait")) {
            run_frames(atol(a1));
        } else if (!strcmp(cmd, "realtime")) {
            // realtime S: keep running frames until S seconds of wall-clock
            // time have passed, for cores that flush saves on a timer
            // (melonDS writes 2 s after the game's last write).
            struct timeval t0, t;
            gettimeofday(&t0, NULL);
            double want = atof(a1);
            do {
                run_frames(1);
                gettimeofday(&t, NULL);
            } while (!shutdown_requested &&
                     (t.tv_sec - t0.tv_sec) + (t.tv_usec - t0.tv_usec) / 1e6 < want);
        } else if (!strcmp(cmd, "press") || !strcmp(cmd, "hold")) {
            int frames = *a2 ? atoi(a2) : 4;
            held = btn_mask(a1, lineno);
            run_frames(frames);
            held = 0;
        } else if (!strcmp(cmd, "press2")) {
            int frames = *a2 ? atoi(a2) : 4;
            held2 = btn_mask(a1, lineno);
            run_frames(frames);
            held2 = 0;
        } else if (!strcmp(cmd, "tap")) {
            // tap BTN [COUNT] [GAP]: press for 4 frames, then wait GAP frames.
            int count = *a2 ? atoi(a2) : 1, gap = *a3 ? atoi(a3) : 12;
            uint32_t m = btn_mask(a1, lineno);
            for (int k = 0; k < count && !shutdown_requested; k++) {
                held = m;
                run_frames(4);
                held = 0;
                run_frames(gap);
            }
        } else if (!strcmp(cmd, "stick") || !strcmp(cmd, "rstick")) {
            // stick X Y FRAMES: hold the left (or right) stick, then centre it.
            int s = cmd[0] == 'r';
            analog[0][s][0] = axis_value(a1);
            analog[0][s][1] = axis_value(a2);
            run_frames(*a3 ? atol(a3) : 4);
            analog[0][s][0] = analog[0][s][1] = 0;
        } else if (!strcmp(cmd, "touch")) {
            // touch X Y [N]: press the touchscreen at frame pixel (X, Y) for N
            // frames. Coordinates are in the whole frame as `shot` writes it, so
            // on a DS (two screens stacked) the bottom screen starts at y = 192.
            unsigned w = fb_w ? fb_w : av.geometry.base_width;
            unsigned h = fb_h ? fb_h : av.geometry.base_height;
            double x = atof(a1), y = atof(a2);
            ptr_x = (int16_t)((x + 0.5) * 65534.0 / w - 32767.0);
            ptr_y = (int16_t)((y + 0.5) * 65534.0 / h - 32767.0);
            ptr_down = true;
            run_frames(*a3 ? atol(a3) : 6);
            ptr_down = false;
            run_frames(2);
        } else if (!strcmp(cmd, "key")) {
            int frames = *a2 ? atoi(a2) : 4;
            int codes[8], nc = 0;
            char buf[400];
            snprintf(buf, sizeof buf, "%s", a1);
            for (char *tok = strtok(buf, "+"); tok && nc < 8; tok = strtok(NULL, "+"))
                codes[nc++] = key_code(tok, lineno);
            for (int k = 0; k < nc; k++) key_event(codes[k], true);
            run_frames(frames);
            for (int k = nc - 1; k >= 0; k--) key_event(codes[k], false);
            run_frames(2);
        } else if (!strcmp(cmd, "type")) {
            // type TEXT: one key per character, '_' for a space.
            for (char *c = a1; *c && !shutdown_requested; c++) {
                char one[2] = {*c == '_' ? ' ' : *c, 0};
                int code = one[0] == ' ' ? 32 : key_code(one, lineno);
                bool shift = (*c >= 'A' && *c <= 'Z');
                if (shift) key_event(304, true);
                key_event(code, true);
                run_frames(4);
                key_event(code, false);
                if (shift) key_event(304, false);
                run_frames(4);
            }
        } else if (!strcmp(cmd, "flip") || !strcmp(cmd, "disk") || !strcmp(cmd, "eject") ||
                   !strcmp(cmd, "insert")) {
            // Through the core's disk control interface (multi-disc CDs, FDS
            // sides). flip: image index ^ 1. disk N [FRAMES]: eject, wait,
            // select image N (0-based), wait, insert. Cores without the
            // interface change sides with their own buttons; press those.
            if (!have_disk_cb) {
                fprintf(stderr, "line %d: the core has no disk control interface\n", lineno);
                exit(1);
            }
            if (!strcmp(cmd, "eject")) disk_cb.set_eject_state(true);
            else if (!strcmp(cmd, "insert")) disk_cb.set_eject_state(false);
            else {
                unsigned cur = disk_cb.get_image_index();
                unsigned want = !strcmp(cmd, "flip") ? cur ^ 1 : (unsigned)atoi(a1);
                long gap = (!strcmp(cmd, "disk") && *a2) ? atol(a2) : 30;
                bool ok = disk_cb.set_eject_state(true);
                run_frames(gap);
                ok = disk_cb.set_image_index(want) && ok;
                run_frames(gap);
                ok = disk_cb.set_eject_state(false) && ok;
                note("  [disk] image %u -> %u of %u, ok=%d\n", cur, disk_cb.get_image_index(),
                     disk_cb.get_num_images(), ok);
            }
        } else if (!strcmp(cmd, "repeat")) {
            int count = atoi(a1);
            int end = find_end(i + 1);
            for (int k = 0; k < count && !shutdown_requested; k++) run_lines(i + 1, end);
            i = end;
        } else if (!strcmp(cmd, "end")) {
            // closes a repeat; reached only when stepping past a body
        } else if (!strcmp(cmd, "shot")) {
            do_shot(a1);
        } else if (!strcmp(cmd, "dump")) {
            dump_mem(MEM_SAVE_RAM, a1);
        } else if (!strcmp(cmd, "dumprtc")) {
            dump_mem(MEM_RTC, a1);
        } else if (!strcmp(cmd, "ram")) {
            dump_mem(MEM_SYSTEM_RAM, a1);
        } else if (!strcmp(cmd, "srm")) {
            load_mem(MEM_SAVE_RAM, a1);
        } else if (!strcmp(cmd, "savestate")) {
            save_state(a1);
        } else if (!strcmp(cmd, "loadstate")) {
            load_state(a1);
        } else if (!strcmp(cmd, "reset")) {
            retro_reset();
        } else if (!strcmp(cmd, "echo")) {
            note("  [frame %ld] %s %s %s\n", frame_no, a1, a2, a3);
        } else if (!strcmp(cmd, "quit")) {
            return;
        } else {
            fprintf(stderr, "line %d: no such command '%s'\n", lineno, cmd);
            exit(1);
        }
    }
}

// --- saves, the RetroArch way --------------------------------------------

static char stem[1024];

static void slot_stem(const char *p, char *out, size_t n) {
    const char *b = strrchr(p, '/');
    b = b ? b + 1 : p;
    snprintf(out, n, "%s", b);
    char *dot = strrchr(out, '.');
    if (dot && dot != out) *dot = 0;
}

static void write_saves(void) {
    char path[2048];
    if (subsys_used) {
        // RetroArch (runloop_path_init_subsystem): one file per memory of each
        // loaded slot, named after that slot's file; no .srm/.rtc of its own.
        for (unsigned i = 0; i < n_slots && i < subsys_used->num_roms; i++) {
            const struct retro_subsystem_rom_info *r = &subsys_used->roms[i];
            char st[1024];
            slot_stem(slot_paths[i], st, sizeof st);
            for (unsigned j = 0; j < r->num_memory; j++) {
                void *d = retro_get_memory_data(r->memory[j].type);
                size_t n = retro_get_memory_size(r->memory[j].type);
                if (!d || !n) {
                    note("  slot %u memory 0x%x (%s): none\n", i, r->memory[j].type, r->memory[j].extension);
                    continue;
                }
                snprintf(path, sizeof path, "%s/%s.%s", savedir, st, r->memory[j].extension);
                if (write_file(path, d, n)) note("  wrote %s (%zu bytes, memory 0x%x)\n", path, n, r->memory[j].type);
            }
        }
        return;
    }
    struct {
        unsigned id;
        const char *ext;
    } regions[] = {{MEM_SAVE_RAM, "srm"}, {MEM_RTC, "rtc"}};
    for (size_t r = 0; r < 2; r++) {
        void *d = retro_get_memory_data(regions[r].id);
        size_t n = retro_get_memory_size(regions[r].id);
        if (!d || !n) continue;
        snprintf(path, sizeof path, "%s/%s.%s", savedir, stem, regions[r].ext);
        if (write_file(path, d, n)) note("  wrote %s (%zu bytes)\n", path, n);
    }
}

static void usage(const char *argv0) {
    fprintf(stderr,
            "usage: %s --core CORE --rom ROM [options]\n"
            "\n"
            "  --core CORE      libretro core to open\n"
            "  --rom ROM        the game to load (a path; cores get bytes too)\n"
            "  --savedir DIR    the core's save directory; .srm/.rtc land here (default .)\n"
            "  --sysdir DIR     the core's system (BIOS) directory (default .)\n"
            "  --shots DIR      where screenshots go (default .)\n"
            "  --options FILE   core options, key = value per line\n"
            "  --info FILE      write what ran (core, version, frames, sizes) as JSON\n"
            "  --srm SAVE       battery save to load before the script runs\n"
            "  --rtc FILE       clock region to load before the script runs\n"
            "  --state FILE     save state to load before the script runs\n"
            "  --script FILE    commands to run, or - for stdin\n"
            "  --no-write       do not write .srm/.rtc on exit\n"
            "  --no-hw          refuse a hardware-rendered context\n"
            "  --pad2           plug the --device pad into port 2 as well (default: a joypad)\n"
            "  --ports N        ports to plug a pad into (default 2; RetroArch plugs one into\n"
            "                   every port; 1 is the old behaviour of port 1 only)\n"
            "  --pace FPS       run at most FPS frames per wall-clock second (cores that\n"
            "                   emulate on their own real-time thread, e.g. ARMSX2)\n"
            "  --subsystem ID   load ROM plus --slot FILE... through retro_load_game_special\n"
            "                   (Sufami Turbo, ...); saves are named after each slot's file\n"
            "  --slot FILE      a further subsystem slot, in order (- leaves it empty)\n"
            "  --list-subsystems  print the core's subsystems and exit\n"
            "  --device ID      libretro device for the pads (default 1, joypad; a\n"
            "                   DualShock is usually 0x305, analog subclass 2)\n"
            "  --quiet          only report errors\n"
            "\n"
            "script commands:\n"
            "  wait N                 run N frames with no input\n"
            "  realtime S             run frames until S wall-clock seconds pass\n"
            "  press BTN[+BTN] [N]    hold buttons for N frames (default 4), then release\n"
            "  press2 BTN[+BTN] [N]   the same on controller 2\n"
            "  tap BTN [COUNT] [GAP]  press 4 frames then wait GAP (default 12), COUNT times\n"
            "  stick X Y [N]          hold the left stick (min/max/-32767..32767) N frames\n"
            "  rstick X Y [N]         the same for the right stick\n"
            "  key KEY[+KEY] [N]      hold keyboard keys N frames (a-z 0-9 return space f1..,\n"
            "                         kcN for raw libretro keycode N)\n"
            "  touch X Y [N]          touch the screen at frame pixel X,Y for N frames (6)\n"
            "  type TEXT              type characters, '_' for a space\n"
            "  flip                   turn the disk over (disk control interface)\n"
            "  disk N [FRAMES]        eject, select image N (0-based), insert\n"
            "  eject / insert         open or close the drive\n"
            "  repeat N ... end       run the enclosed lines N times\n"
            "  include FILE           splice another script in, relative to this one\n"
            "  shot [NAME]            write a PNG to --shots\n"
            "  dump PATH              write battery save RAM now\n"
            "  dumprtc PATH           write the clock region now\n"
            "  ram PATH               write system RAM\n"
            "  srm PATH               load battery save RAM mid-run\n"
            "  savestate PATH         write a save state\n"
            "  loadstate PATH         load a save state\n"
            "  reset                  reset the machine\n"
            "  echo TEXT              print to stderr with the frame number\n"
            "  quit                   stop the script here\n"
            "\n"
            "buttons: b y select start up down left right a x l r l2 r2 l3 r3\n",
            argv0);
}

int main(int argc, char **argv) {
    const char *rom = NULL, *srm = NULL, *rtc = NULL, *state = NULL, *script = NULL;
    const char *options = NULL, *info = NULL;
    const char *subsystem = NULL, *slot_extra[MAX_SLOTS];
    unsigned n_extra = 0;
    bool list_subsystems = false;
    bool no_write = false, pad2 = false;
    unsigned ports = 2;
    unsigned device = DEV_JOYPAD;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--core") && i + 1 < argc) core_path = argv[++i];
        else if (!strcmp(argv[i], "--rom") && i + 1 < argc) rom = argv[++i];
        else if (!strcmp(argv[i], "--savedir") && i + 1 < argc) savedir = argv[++i];
        else if (!strcmp(argv[i], "--sysdir") && i + 1 < argc) sysdir = argv[++i];
        else if (!strcmp(argv[i], "--shots") && i + 1 < argc) shots_dir = argv[++i];
        else if (!strcmp(argv[i], "--out") && i + 1 < argc) shots_dir = argv[++i];
        else if (!strcmp(argv[i], "--options") && i + 1 < argc) options = argv[++i];
        else if (!strcmp(argv[i], "--info") && i + 1 < argc) info = argv[++i];
        else if (!strcmp(argv[i], "--srm") && i + 1 < argc) srm = argv[++i];
        else if (!strcmp(argv[i], "--rtc") && i + 1 < argc) rtc = argv[++i];
        else if (!strcmp(argv[i], "--state") && i + 1 < argc) state = argv[++i];
        else if (!strcmp(argv[i], "--script") && i + 1 < argc) script = argv[++i];
        else if (!strcmp(argv[i], "--no-write")) no_write = true;
        else if (!strcmp(argv[i], "--no-hw")) want_hw = false;
        else if (!strcmp(argv[i], "--pace") && i + 1 < argc) pace_fps = atof(argv[++i]);
        else if (!strcmp(argv[i], "--pad2")) pad2 = true;
        else if (!strcmp(argv[i], "--ports") && i + 1 < argc) ports = (unsigned)strtoul(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--device") && i + 1 < argc) device = (unsigned)strtoul(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--quiet")) quiet = true;
        else if (!strcmp(argv[i], "--subsystem") && i + 1 < argc) subsystem = argv[++i];
        else if (!strcmp(argv[i], "--slot") && i + 1 < argc && n_slots + 1 < MAX_SLOTS) slot_extra[n_extra++] = argv[++i];
        else if (!strcmp(argv[i], "--list-subsystems")) list_subsystems = true;
        else if (!strcmp(argv[i], "--subsystem-id") && i + 1 < argc) subsys_id_override = (unsigned)strtoul(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "-h") || !strcmp(argv[i], "--help")) {
            usage(argv[0]);
            return 0;
        } else {
            usage(argv[0]);
            return 2;
        }
    }
    if (!*core_path || !rom) {
        usage(argv[0]);
        return 2;
    }
    mkdir(shots_dir, 0755);
    mkdir(savedir, 0755);
    if (options) load_options(options);
    if (script) read_script(script, 0);

    // RetroArch names saves after the content's file name, extension dropped.
    const char *base = strrchr(rom, '/');
    base = base ? base + 1 : rom;
    snprintf(stem, sizeof stem, "%s", base);
    char *dot = strrchr(stem, '.');
    if (dot && dot != stem) *dot = 0;

    // RetroArch's order: system info, environment, init, then the other
    // callbacks. Mesen and the rust-libretro cores crash in any other.
    bind_core(core_path);
    struct retro_system_info si = {0};
    retro_get_system_info(&si);
    retro_set_environment(cb_env);
    retro_init();
    retro_set_video_refresh(cb_video);
    retro_set_audio_sample(cb_audio_sample);
    retro_set_audio_sample_batch(cb_audio_batch);
    retro_set_input_poll(cb_input_poll);
    retro_set_input_state(cb_input_state);

    void *rd = NULL;
    if (list_subsystems) {
        for (unsigned s = 0; s < n_subsys; s++) {
            printf("subsystem %s (\"%s\", id 0x%x)\n", subsys[s].ident, subsys[s].desc ? subsys[s].desc : "", subsys[s].id);
            for (unsigned r = 0; r < subsys[s].num_roms; r++) {
                const struct retro_subsystem_rom_info *ri = &subsys[s].roms[r];
                printf("  slot %u: %s [%s]%s%s\n", r, ri->desc, ri->valid_extensions ? ri->valid_extensions : "",
                       ri->required ? " required" : "", ri->need_fullpath ? " fullpath" : "");
                for (unsigned j = 0; j < ri->num_memory; j++)
                    printf("    memory .%s type 0x%x\n", ri->memory[j].extension, ri->memory[j].type);
            }
        }
        if (!n_subsys) printf("no subsystems\n");
        return 0;
    }
    if (subsystem) {
        for (unsigned s = 0; s < n_subsys; s++)
            if (!strcmp(subsys[s].ident, subsystem) || (subsys[s].desc && !strcmp(subsys[s].desc, subsystem)))
                subsys_used = &subsys[s];
        if (!subsys_used) {
            fprintf(stderr, "the core has no subsystem %s\n", subsystem);
            return 1;
        }
        slot_paths[n_slots++] = rom;
        for (unsigned k = 0; k < n_extra; k++) slot_paths[n_slots++] = slot_extra[k];
        struct retro_game_info sgi[MAX_SLOTS];
        void *sdata[MAX_SLOTS] = {0};
        for (unsigned k = 0; k < n_slots; k++) {
            sgi[k] = (struct retro_game_info){.path = slot_paths[k], .data = NULL, .size = 0, .meta = NULL};
            if (!strcmp(slot_paths[k], "-")) { sgi[k].path = NULL; continue; }
            if (!subsys_used->roms[k].need_fullpath) {
                size_t rn = 0;
                sdata[k] = read_file(slot_paths[k], &rn);
                if (!sdata[k]) { perror(slot_paths[k]); return 1; }
                sgi[k].data = sdata[k];
                sgi[k].size = rn;
            }
        }
        unsigned gtype = subsys_id_override ? subsys_id_override : subsys_used->id;
        note("  retro_load_game_special(0x%x, %u files)\n", gtype, n_slots);
        if (!retro_load_game_special(gtype, sgi, n_slots)) {
            fprintf(stderr, "the core refused subsystem %s\n", subsystem);
            return 1;
        }
        note("  loaded subsystem %s with %u files\n", subsys_used->ident, n_slots);
        goto loaded;
    }
    struct retro_game_info gi = {.path = rom, .data = NULL, .size = 0, .meta = NULL};
    if (!si.need_fullpath) {
        size_t rn = 0;
        rd = read_file(rom, &rn);
        if (!rd) {
            perror(rom);
            return 1;
        }
        gi.data = rd;
        gi.size = rn;
    }
    if (!retro_load_game(&gi)) {
        fprintf(stderr, "the core refused %s\n", rom);
        return 1;
    }
loaded:
    // RetroArch plugs a pad into every port up to its user count; some cores (bsnes-jg)
    // crash when port 2 has nothing. Port 1 gets --device; the others a joypad, or
    // --device too with --pad2.
    if (pad2 && ports < 2) ports = 2;
    for (unsigned p = 0; p < ports && p < 8; p++)
        retro_set_controller_port_device(p, p == 0 || pad2 ? device : 1);

    retro_get_system_av_info(&av);
#ifdef HAVE_CGL
    if (hw_active) {
        unsigned w = av.geometry.max_width, h = av.geometry.max_height;
        if (w < 640) w = 640;
        if (h < 480) h = 480;
        gl_make_fbo(w, h);
        if (hw.context_reset) hw.context_reset();
    }
#endif
    note("%s %s: %ux%u @ %.2f fps, save RAM %zu bytes, RTC %zu bytes, %s\n",
         si.library_name ? si.library_name : "core",
         si.library_version ? si.library_version : "?", av.geometry.base_width,
         av.geometry.base_height, av.timing.fps, retro_get_memory_size(MEM_SAVE_RAM),
         retro_get_memory_size(MEM_RTC), hw_active ? "OpenGL" : "software");

    if (srm) load_mem(MEM_SAVE_RAM, srm);
    if (rtc) load_mem(MEM_RTC, rtc);
    if (state) {
        run_frames(1); // some cores refuse a state before their first frame
        load_state(state);
    }
    if (script) run_lines(0, nlines);

    if (!no_write) write_saves();
    if (info) {
        FILE *f = fopen(info, "w");
        if (f) {
            fprintf(f, "{\"library_name\": \"%s\", \"library_version\": \"%s\", \"frames\": %ld, "
                       "\"save_ram_size\": %zu, \"rtc_size\": %zu, \"renderer\": \"%s\", "
                       "\"stem\": \"%s\"}\n",
                    si.library_name ? si.library_name : "", si.library_version ? si.library_version : "",
                    frame_no, retro_get_memory_size(MEM_SAVE_RAM), retro_get_memory_size(MEM_RTC),
                    hw_active ? "opengl" : "software", stem);
            fclose(f);
        }
    }
#ifdef HAVE_CGL
    if (hw_active && hw.context_destroy) hw.context_destroy();
#endif
    retro_unload_game();
    retro_deinit();
    free(rd);
    note("done after %ld frames\n", frame_no);
    return 0;
}
