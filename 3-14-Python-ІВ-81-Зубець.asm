main:
    push ebp
    mov ebp, esp
    mov eax, 3
    push eax
    mov eax, 2
    pop ebx
    add eax, ebx
    mov [ebp + 4], eax
    mov eax, 1
    mov [ebp + 8], eax
    mov eax, 1
    push eax
    mov eax, [ebp + 4]
    pop ebx
    add eax, ebx
    not eax
    push eax
    mov eax, 2
    push eax
    pop ebx
    pop eax
    sub eax, ebx
    push eax
    mov eax, 2
    push eax
    pop ebx
    pop eax
    mov cl, bl
    sar eax, cl
    mov esp, ebp
    pop ebp
    ret