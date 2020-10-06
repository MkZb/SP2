main:
   mov eax, 3
   not eax
   push eax
   mov eax, 2
   push eax
   mov eax, 1
   not eax
   pop ebx
   add eax, ebx
   pop ebx
   add eax, ebx
   not eax
   ret