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
myF   PROTO STDCALL

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
    mov eax, 2
    push eax
    mov eax, 1
    push eax
    call myF
    add esp, 0
    pop ebp
    ret
main ENDP

myF PROC
    push ebp
    mov ebp, esp
    mov eax, [ebp +8]
    push eax
    mov eax, [ebp +12]
    push eax
    pop ebx
    pop eax
    cmp eax, ebx
    mov eax, 0
    setl al
    cmp eax, 0
    je @cond_false1
    mov eax, [ebp +8]
    push eax
    jmp @cond_end1
@cond_false1:
    mov eax, [ebp +12]
    push eax
@cond_end1:
    pop eax
    sub esp, 4
    mov [ebp -4], eax
    mov eax, [ebp -4]
    sub esp, 4
    mov [ebp -8], eax
    mov eax, 0
    sub esp, 4
    mov [ebp -12], eax
@while_start1:
    mov eax, [ebp -8]
    push eax
    mov eax, 0
    push eax
    pop ebx
    pop eax
    cmp eax, ebx
    mov eax, 0
    setg al
    cmp eax, 0
    je @while_end1
    mov eax, [ebp -4]
    push eax
    mov eax, [ebp -8]
    push eax
    mov edx, 0
    pop ebx
    pop eax
    div ebx
    mov eax, edx
    push eax
    mov eax, 0
    push eax
    pop ebx
    pop eax
    cmp eax, ebx
    mov eax, 0
    sete al
    cmp eax, 0
    je @c2
    mov eax, [ebp -12]
    push eax
    mov eax, [ebp -8]
    pop ebx
    add eax, ebx
    mov [ebp -12], eax
    jmp @end1
@c2:
@end1:
    mov eax, [ebp -8]
    push eax
    mov eax, 1
    push eax
    pop ebx
    pop eax
    sub eax, ebx
    mov [ebp -8], eax
    jmp @while_start1
@while_end1:
    mov eax, [ebp -12]
    add esp, 12
    pop ebp
    ret 8
myF ENDP

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