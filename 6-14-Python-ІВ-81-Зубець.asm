.586
.model flat, stdcall
option casemap:none

include     \masm32\include\windows.inc
include     \masm32\include\kernel32.inc
include     \masm32\include\masm32.inc
include     \masm32\include\user32.inc

includelib  \masm32\lib\kernel32.lib
includelib  \masm32\lib\masm32.lib
includelib  \masm32\lib\user32.lib

NumbToStr   PROTO :DWORD,:DWORD
main   PROTO STDCALL

.data
buff        db 11 dup(?)

.code
start:
    invoke  main
    invoke  NumbToStr, eax, ADDR buff
    invoke  StdOut, eax
    invoke  ExitProcess, 0

main PROC
    push ebp
    mov ebp, esp
    mov eax, 3
    push eax
    mov eax, 1
    push eax
    mov eax, 5
    pop ebx
    add eax, ebx
    push eax
    pop ebx
    pop eax
    mov cl, bl
    sar eax, cl
    add esp, 0
    pop ebp
    ret
main ENDP

NumbToStr PROC uses ebx x:DWORD,buffer:DWORD
    mov     ecx,buffer
    mov     eax,x
    mov     ebx,10
    add     ecx,ebx
@@:
    xor     edx,edx
    div     ebx
    add     edx,48
    mov     BYTE PTR [ecx],dl
    dec     ecx
    test    eax,eax
    jnz     @b
    inc     ecx
    mov     eax,ecx
    ret
NumbToStr ENDP

END start