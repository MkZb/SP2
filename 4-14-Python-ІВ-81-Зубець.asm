main:
    push ebp
    mov ebp, esp
    mov eax, 130
    push eax
    mov eax, 1
    pop ebx
    add eax, ebx
    push eax
    mov eax, 2
    push eax
    pop ebx
    pop eax
    mov cl, bl
    sar eax, cl
    cmp eax, 0
    je c1
    mov eax, 10
    mov [ebp + 4], eax
    mov eax, [ebp + 4]
    cmp eax, 0
    je c2
    mov eax, [ebp + 4]
    jmp end2
c2:
    mov eax, 5
    mov [ebp + 8], eax
end2:
    jmp end1
c1:
    mov eax, 13
    push eax
    mov eax, 5
    push eax
    pop ebx
    pop eax
    mov cl, bl
    sar eax, cl
    cmp eax, 0
    je c3
    mov eax, 100
    jmp end1
c3:
    mov eax, 5
    mov [ebp + 4], eax
    mov eax, [ebp + 4]
end1:
    mov esp, ebp
    pop ebp
    ret