/* sendkey.exe VK: posts WM_KEYDOWN/WM_KEYUP of a virtual key (hex) to Project64's main window. */
typedef void *HWND; typedef int BOOL; typedef unsigned int UINT; typedef unsigned long WPARAM; typedef long LPARAM;
#define WINAPI __stdcall
__declspec(dllimport) BOOL WINAPI EnumWindows(BOOL (WINAPI *)(HWND, LPARAM), LPARAM);
__declspec(dllimport) int WINAPI GetWindowTextA(HWND, char *, int);
__declspec(dllimport) void *WINAPI GetMenu(HWND);
__declspec(dllimport) BOOL WINAPI PostMessageA(HWND, UINT, WPARAM, LPARAM);
__declspec(dllimport) char *WINAPI GetCommandLineA(void);
__declspec(dllimport) void WINAPI ExitProcess(UINT);
static HWND found;
static BOOL WINAPI cb(HWND h, LPARAM l) {
  char t[256]; int n = GetWindowTextA(h, t, 256);
  for (int i = 0; i + 9 <= n; i++) {
    const char *p = "Project64"; int j = 0;
    while (j < 9 && t[i + j] == p[j]) j++;
    if (j == 9 && GetMenu(h)) { found = h; return 0; }
  }
  return 1;
}
void start(void) {
  char *c = GetCommandLineA(); unsigned vk = 0;
  /* last token, hex */
  char *last = c; for (char *p = c; *p; p++) if (*p == ' ' && p[1] && p[1] != ' ') last = p + 1;
  for (char *p = last; *p; p++) {
    char d = *p; unsigned v = d >= '0' && d <= '9' ? d - '0' : d >= 'a' && d <= 'f' ? d - 'a' + 10 : d >= 'A' && d <= 'F' ? d - 'A' + 10 : 99;
    if (v == 99) break; vk = vk * 16 + v;
  }
  EnumWindows(cb, 0);
  if (!found || !vk) ExitProcess(1);
  PostMessageA(found, 0x100, vk, 1);
  PostMessageA(found, 0x101, vk, 0xC0000001);
  ExitProcess(0);
}
