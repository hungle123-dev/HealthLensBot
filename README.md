## 📖 Giới thiệu (Introduction)

**HealthLensBot** là một trợ lý dinh dưỡng được vận hành bởi AI, kết hợp sức mạnh của các mô hình thị giác (Vision Models) tiên tiến và xử lý ngôn ngữ tự nhiên. Ứng dụng giúp bạn tự động nhận diện nguyên liệu từ hình ảnh món ăn, phân tích giá trị dinh dưỡng, kiểm tra sự phù hợp với chế độ ăn kiêng và gợi ý công thức nấu ăn cá nhân hóa.

---

## ✨ Tính năng nổi bật (Features)

- **🔍 Ingredient Detection:** Nhận diện chính xác các thành phần thực phẩm qua camera/hình ảnh.
- **🛡️ Dietary Filtering:** Tự động loại bỏ các nguyên liệu không phù hợp (Vegan, Keto, Gluten-free, v.v.).
- **📊 Nutrient Analysis:** Phân tích chi tiết Protein, Carbs, Fats, Vitamins và Minerals.
- **🔥 Calorie Estimation:** Ước tính tổng lượng calo trong bữa ăn.
- **👩‍🍳 Recipe Suggestion:** Gợi ý các món ăn sáng tạo dựa trên nguyên liệu sẵn có.
- **⚡ Fast & Secure:** Xử lý nhanh chóng với OpenRouter và bảo mật dữ liệu file tạm.

---

## 🛠️ Công nghệ sử dụng (Tech Stack)

- **Framework:** [CrewAI](https://www.crewai.com/) (Multi-agent orchestration)
- **AI Models:** OpenRouter (Qwen2.5-VL, Llama 3.2 via OpenRouter)
- **UI:** [Gradio](https://gradio.app/)
- **Language:** Python 3.10+

---

## 🚀 Cài đặt (Installation)

### 1. Chuẩn bị
- Python 3.10 trở lên.
- Git.

### 2. Các bước thực hiện
```bash
# Clone project
git clone https://github.com/hungle123-dev/HealthLensBot.git HealthLensBot
cd HealthLensBot

# Tạo môi trường ảo (Khuyên dùng)
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Cấu hình API
Tạo file `.env` tại thư mục gốc và thêm key của bạn:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

## 💻 Cách sử dụng (Usage)

Khởi động giao diện web:
```bash
python app.py
```
Sau đó truy cập địa chỉ `http://127.0.0.1:5000` trên trình duyệt để bắt đầu trải nghiệm.

---

## 📂 Cấu trúc thư mục (File Structure)

```text
HealthLensBot/
├── app.py              # File chạy chính (Gradio UI)
├── src/
│   ├── config.py       # Cấu hình môi trường & Client API
│   ├── crew.py         # Định nghĩa Agents & Tasks
│   ├── tools.py        # Các công cụ AI (Vision, Filter)
│   ├── formatters.py   # Xử lý hiển thị Markdown
│   └── models.py       # Định nghĩa Pydantic Models
├── assets/             # Hình ảnh & Logo
├── examples/           # Ảnh mẫu để test
├── .env                # File cấu hình bí mật (Không upload lên Git)
└── requirements.txt    # Danh sách thư viện
```

---

## 🤝 Đóng góp
- **Tác giả:** [Lê Võ Xuân HƯng](mailto:hunglecrkh2k5@gmail.com)
