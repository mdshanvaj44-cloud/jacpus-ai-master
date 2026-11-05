# JACPU-S AI — Master Starter (Hindi)

यह JACPU-S का शुरुआती, एकीकृत प्रोजेक्ट है। इसमें हल्का मोबाइल वेब ऐप और Python FastAPI backend शामिल हैं।

## अभी क्या काम करता है
- मोबाइल-फ्रेंडली AI Studio UI
- प्रोजेक्ट बनाना और सूची देखना
- फाइल/कोड को छोटे हिस्सों में सेव करना
- AI provider के OpenAI-compatible Chat Completions API से server-side request
- health check और cloud-session placeholder
- HTML गेम का छोटा स्थानीय preview (iframe)

## अभी क्या नहीं है
- यह कोई अपना प्रशिक्षित AI model नहीं है।
- यह करोड़ों शब्द एक ही request में नहीं लिखता; बड़े प्रोजेक्ट को फाइलों और छोटे हिस्सों में बनाता है।
- इसमें GPU मशीन, Unreal/Unity/Godot build farm, WebRTC streaming server या GTA-जैसे गेम का runtime शामिल नहीं है।
- Render Free CPU service, AAA cloud gaming GPU नहीं है। GPU बाद में अलग provider पर जोड़ना होगा।
- शुरुआती storage SQLite है। Render Free की local disk स्थायी नहीं मानी जानी चाहिए; production से पहले persistent database/object storage जोड़ें।

## GitHub + Render (मोबाइल से)
1. ZIP extract करें।
2. GitHub पर नया **Private** repository बनाएं।
3. ZIP के अंदर की सभी files/folders repository के root में upload करें।
4. Render Dashboard → New → Blueprint → GitHub repo चुनें।
5. Render `render.yaml` पढ़कर web service बनाएगा।
6. Deploy पूरा होने पर `https://YOUR-SERVICE.onrender.com/health` खोलें।
7. ऐप का `frontend/index.html` खोलें, Settings में Backend URL डालें।

## Render Environment Variables
- `APP_SECRET`: Render dashboard में लंबा random secret सेट करें। इसे किसी से साझा न करें।
- `AI_BASE_URL`: (वैकल्पिक) provider का OpenAI-compatible base URL, जैसे `https://api.openai.com/v1`
- `AI_MODEL`: (वैकल्पिक) मॉडल नाम
- `AI_API_KEY`: (वैकल्पिक) provider API key — केवल Render Environment में रखें, HTML/GitHub में कभी नहीं।

## Free tier और खर्च
केवल Free service चुनें। Paid plan/upgrade न करें। AI API की अपनी billing/limits हो सकती हैं; API key जोड़ने से पहले provider की कीमत जांचें। GPU streaming इस starter में free या enabled नहीं है।

## API routes
- `GET /health`
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/{project_id}/files`
- `PUT /api/projects/{project_id}/files/{file_path:path}`
- `POST /api/ai/chat`
- `POST /api/sessions` (GPU not configured placeholder)
- `POST /api/sessions/{session_id}/stop`
- `GET /docs` (API documentation)

## सुरक्षा
- API key server-side environment variable में रखें।
- `APP_SECRET` बदलें; demo default को production में न छोड़ें।
- GitHub repository private रखें।
- कोई password, OTP या API key चैट में न भेजें।
