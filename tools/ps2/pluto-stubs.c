// Stand-ins for libplutovg.1 / libplutosvg.0, which the armsx2 buildbot core links from the
// build machine's .deps. They draw SVG icons for PCSX2's own on-screen UI, which a libretro
// frontend never shows: every call fails (NULL / 0), as if the SVG could not be parsed.
#include <stddef.h>
#ifdef PLUTOSVG
void *plutosvg_document_load_from_data(const char *d, int n, float w, float h, void *destroy, void *closure) { (void)d; (void)n; (void)w; (void)h; (void)destroy; (void)closure; return NULL; }
void plutosvg_document_destroy(void *doc) { (void)doc; }
float plutosvg_document_get_width(const void *doc) { (void)doc; return 0; }
float plutosvg_document_get_height(const void *doc) { (void)doc; return 0; }
int plutosvg_document_render(const void *doc, const char *id, void *canvas, const void *color, void *cb, void *closure) { (void)doc; (void)id; (void)canvas; (void)color; (void)cb; (void)closure; return 0; }
const void *plutosvg_ft_svg_hooks(void) { return NULL; }
#else
void *plutovg_canvas_create(void *surface) { (void)surface; return NULL; }
void plutovg_canvas_destroy(void *c) { (void)c; }
void plutovg_canvas_scale(void *c, float x, float y) { (void)c; (void)x; (void)y; }
void plutovg_canvas_translate(void *c, float x, float y) { (void)c; (void)x; (void)y; }
void plutovg_convert_argb_to_rgba(unsigned char *dst, const unsigned char *src, int w, int h, int stride) { (void)dst; (void)src; (void)w; (void)h; (void)stride; }
void *plutovg_surface_create_for_data(unsigned char *data, int w, int h, int stride) { (void)data; (void)w; (void)h; (void)stride; return NULL; }
void plutovg_surface_destroy(void *s) { (void)s; }
#endif
