<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>منصتي المتكاملة</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; background: #2c3e50; color: white; padding: 20px; transition: 0.5s; }
        .box { background: #34495e; padding: 20px; border-radius: 15px; margin: 10px; display: inline-block; width: 300px; vertical-align: top; }
        button { display: block; width: 100%; padding: 12px; margin: 5px 0; font-size: 16px; cursor: pointer; border: none; border-radius: 8px; background: #e67e22; color: white; }
        button:hover { background: #d35400; }
        #display { font-size: 22px; font-weight: bold; margin-top: 20px; padding: 20px; background: #ecf0f1; color: #2c3e50; border-radius: 10px; }
    </style>
</head>
<body>

    <h1>مركز الترفيه والتحكم</h1>

    <div class="box">
        <h3>الألعاب</h3>
        <button onclick="playGame('حجر')">لعبة: حجر ورقة مقص</button>
        <button onclick="guessNumber()">لعبة: خمن الرقم (1-10)</button>
    </div>

    <div class="box">
        <h3>الأدوات</h3>
        <button onclick="showTime()">عرض الوقت</button>
        <button onclick="changeColor()">تغيير لون الخلفية</button>
        <button onclick="resetScore()">تصفير النقاط</button>
    </div>

    <div id="display">اضغط على أي زر للبدء</div>
    <div id="score">النقاط: 0</div>

    <script>
        let score = 0;

        function updateDisplay(text) {
            document.getElementById('display').innerText = text;
        }

        // 1. لعبة حجر ورقة مقص
        function playGame(userChoice) {
            const choices = ['حجر', 'ورقة', 'مقص'];
            const botChoice = choices[Math.floor(Math.random() * choices.length)];
            if (userChoice === botChoice) updateDisplay("تعادل! الكمبيوتر اختار " + botChoice);
            else if ((userChoice === 'حجر' && botChoice === 'مقص') || (userChoice === 'ورقة' && botChoice === 'حجر') || (userChoice === 'مقص' && botChoice === 'ورقة')) {
                score++;
                updateDisplay("فزت! الكمبيوتر اختار " + botChoice);
            } else {
                score--;
                updateDisplay("خسرت! الكمبيوتر اختار " + botChoice);
            }
            document.getElementById('score').innerText = "النقاط: " + score;
        }

        // 2. لعبة التخمين
        function guessNumber() {
            const num = Math.floor(Math.random() * 10) + 1;
            updateDisplay("تم توليد رقم جديد.. حاول تخمينه! (الرقم هو " + num + ")");
        }

        // 3. الأدوات
        function showTime() {
            updateDisplay("الوقت الآن: " + new Date().toLocaleTimeString('ar-SA'));
        }

        function changeColor() {
            const randomColor = '#' + Math.floor(Math.random()*16777215).toString(16);
            document.body.style.backgroundColor = randomColor;
        }

        function resetScore() {
            score = 0;
            document.getElementById('score').innerText = "النقاط: 0";
            updateDisplay("تم تصفير النقاط!");
        }
    </script>
</body>
</html>
