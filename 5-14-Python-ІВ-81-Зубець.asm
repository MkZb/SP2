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
myFunc   PROTO STDCALL

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
    mov eax, 100
    push eax
    mov eax, 6
    pop ebx
    add eax, ebx
    sub esp, 4
    mov [ebp -4], eax
    mov eax, 5
    push eax
    pop ebx
    mov eax, [ebp -4]
    mov cl, bl
    sar eax, cl
    mov [ebp -4], eax
    mov eax, [ebp -4]
    cmp eax, 0
    je c1
    mov eax, 3
    push eax
    mov eax, 2
    push eax
    mov eax, 1
    push eax
    call myFunc
    push eax
    mov eax, 23
    push eax
    mov eax, 9
    push eax
    mov eax, 3
    push eax
    mov eax, 100
    push eax
    call myFunc
    pop ebx
    add eax, ebx
    pop ebx
    add eax, ebx
    push eax
    mov eax, 1
    push eax
    pop ebx
    pop eax
    mov cl, bl
    sar eax, cl
    sub esp, 4
    mov [ebp -8], eax
    mov eax, [ebp -8]
    jmp end1
c1:
    mov eax, [ebp -4]
end1:
    add esp, 8
    pop ebp
    ret
main ENDP

myFunc PROC
    push ebp
    mov ebp, esp
    mov eax, 100
    sub esp, 4
    mov [ebp -4], eax
    mov eax, 200
    sub esp, 4
    mov [ebp -8], eax
    mov eax, 5
    push eax
    pop ebx
    mov eax, [ebp -4]
    mov cl, bl
    sar eax, cl
    mov [ebp -4], eax
    mov eax, 3
    sub esp, 4
    mov [ebp -12], eax
    mov eax, [ebp +8]
    push eax
    mov eax, [ebp +12]
    push eax
    mov eax, [ebp +16]
    push eax
    mov eax, [ebp -4]
    pop ebx
    add eax, ebx
    pop ebx
    add eax, ebx
    pop ebx
    add eax, ebx
    add esp, 12
    pop ebp
    ret 12
myFunc ENDP

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