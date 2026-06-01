#!/bin/bash

# 1. تحديد المسار الكامل للمجلد الذي يحتوي على هذا السكريبت وتخزينه في متغير
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 2. تفعيل البيئة الوهمية بالاعتماد على المتغير
source "$SCRIPT_DIR/gate_venv/bin/activate"

# 3. تشغيل تطبيق Flask في الخلفية
python3 "$SCRIPT_DIR/web_app/main.py" &

# 4. الانتظار لثوانٍ حتى يكتمل إقلاع سيرفر Flask
sleep 3

# 5. تشغيل ngrok
# (ملاحظة سريعة: إذا كنت لا تزال تشغّل هذا السكريبت عبر systemd، تذكر إضافة كلمة exec قبل python3 هنا كما ناقشنا سابقاً)
python3 "$SCRIPT_DIR/any/start_ngrok.py"

# 6. إنهاء العمليات
python3 "$SCRIPT_DIR/any/kill.py"