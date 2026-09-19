#Requires AutoHotkey v2.0
#SingleInstance Force

; Hook level remap: Shift + z -> type 'a'
+z::
+Z::
{
    Send("{BackSpace}a")
}
