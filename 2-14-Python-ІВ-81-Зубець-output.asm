main:
   mov eax, 333
   push eax
   mov eax, 3
   push eax
   mov eax, 2
   pop ebx
   add eax, ebx
   not eax
   push eax
   mov eax, 3
   not eax
   push eax
   mov eax, 1231
   pop ebx
   add eax, ebx
   pop ebx
   add eax, ebx
   pop ebx
   add eax, ebx
   ret