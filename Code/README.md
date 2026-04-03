# Word Chain Game - Game nối từ tiếng Việt

Một trò chơi nối từ đa người chơi sử dụng kiến trúc client-server TCP với giao diện desktop GUI.

## 🎯 Mục tiêu

Áp dụng các khái niệm mạng máy tính cơ bản:
- Giao tiếp socket TCP
- Xử lý kết nối đa client
- Truyền tải dữ liệu thời gian thực
- Xác thực phía server

## 🎮 Luật chơi

- Mỗi người chơi nhập một từ tiếng Việt
- Từ tiếp theo phải bắt đầu bằng chữ cái cuối của từ trước
- Từ phải có trong từ điển tiếng Việt
- Server kiểm tra và broadcast cho tất cả người chơi

**Ví dụ chuỗi hợp lệ:** `a` → `an` → `ng` → `ga` → `an`

## 🏗️ Kiến trúc

```
┌─────────────┐    TCP Socket    ┌─────────────┐
│   Client 1  │◄────────────────►│             │
│   (Tkinter) │                  │   Server    │
└─────────────┘                  │ (Threading) │
                                 └─────────────┘
┌─────────────┐                  ┌─────────────┐
│   Client 2  │◄────────────────►│ Dictionary │
│   (Tkinter) │                  │ Validation │
└─────────────┘                  └─────────────┘
```

### Server (word_chain_server.py)
- **TCP Socket Server**: Chấp nhận kết nối đa client
- **Thread-per-Client**: Mỗi client có thread riêng
- **Thread-Safe**: Sử dụng `threading.Lock()` cho dữ liệu chia sẻ
- **Validation**: Kiểm tra quy tắc nối từ + từ điển
- **Broadcast**: Gửi tin nhắn cho tất cả client

### Client (word_chain_client.py)
- **Tkinter GUI**: Giao diện desktop
- **Threading**: Network I/O trong thread riêng (không block GUI)
- **Queue**: Truyền tin nhắn giữa network thread và GUI thread
- **Real-time**: Cập nhật trạng thái game tức thời

### Validation (word_validation.py)
- **Unicode Handling**: Xử lý dấu thanh tiếng Việt (NFC normalization)
- **Chain Rules**: Kiểm tra quy tắc nối từ
- **Dictionary Lookup**: Tra cứu từ điển O(1) với set

## 📁 Cấu trúc file

```
word-chain-game/
├── word_chain_server.py      # Server TCP socket
├── word_chain_client.py       # Client GUI Tkinter
├── word_validation.py         # Utility functions
├── vietnamese_dictionary.txt  # Từ điển tiếng Việt (447 từ)
├── README.md                  # Tài liệu này
└── test_*.py                  # Scripts test
```

## 🚀 Cách chạy

### Bước 1: Khởi động Server
```bash
python word_chain_server.py
```
Server sẽ chạy trên `localhost:5000` và load từ điển.

### Bước 2: Khởi động Client
Mở terminal mới và chạy:
```bash
python word_chain_client.py
```

### Bước 3: Chơi game
1. Nhập tên người chơi
2. Nhập từ tiếng Việt theo quy tắc
3. Xem tin nhắn broadcast từ server

## 🧪 Test

### Test cơ bản
```bash
python test_comprehensive.py
```

### Test đa client
```bash
python test_multi_client.py
```

### Test validation
```bash
python word_validation.py
```

## 🔧 Yêu cầu kỹ thuật

- **Python**: 3.6+
- **Libraries**: Chỉ sử dụng thư viện chuẩn (socket, threading, tkinter, json, unicodedata)
- **Network**: TCP socket trên localhost:5000
- **Encoding**: UTF-8 cho tin nhắn JSON

## 🎨 Tính năng

### ✅ Đã hoàn thành
- [x] Server TCP socket đa client với threading
- [x] Client GUI Tkinter với threading + queue
- [x] Validation quy tắc nối từ
- [x] Validation từ điển tiếng Việt
- [x] Broadcast real-time cho tất cả client
- [x] Quản lý người chơi (join/leave, tên duy nhất)
- [x] Xử lý Unicode tiếng Việt (NFC normalization)
- [x] Xử lý lỗi và disconnect

### 🔄 Có thể mở rộng
- [ ] Đếm điểm và thống kê người chơi
- [ ] Lưu lịch sử game
- [ ] Chat giữa người chơi
- [ ] Timer cho mỗi lượt chơi
- [ ] Game modes khác nhau

## 🐛 Xử lý lỗi

### Server
- Connection timeout: 60 giây
- Thread-safe với `threading.Lock()`
- Graceful shutdown với Ctrl+C

### Client
- Network thread daemon (tự động kết thúc)
- Queue-based IPC giữa threads
- Error handling cho disconnect

### Validation
- Unicode normalization cho tiếng Việt
- Case-insensitive comparison
- Input sanitization

## 📊 Kết quả test

```
=== Word Chain Game - Comprehensive Test ===

=== TEST 1: Single Player Word Chain ===
✓ Player joined
  ✓ Word 1: 'a' accepted (next: a)
  ✓ Word 2: 'an' accepted (next: n)
  ✓ Word 3: 'ng' accepted (next: g)
  ✓ Word 4: 'ga' accepted (next: a)
  ✓ Word 5: 'an' accepted (next: n)

=== TEST 2: Invalid Word Chain Detection ===
  First word 'ba' sent
  ✓ Invalid chain rejected: Word must start with 'n' (last letter of 'an')

=== TEST 3: Player Name Validation ===
  ✓ Empty name rejected
  ✓ Valid name accepted

============================================================
All tests completed!
============================================================
```

## 🎓 Học được gì

1. **Networking**: TCP socket programming, multi-client handling
2. **Concurrency**: Threading, thread-safety, daemon threads
3. **GUI Programming**: Tkinter, event-driven programming
4. **Unicode**: Handling Vietnamese characters and normalization
5. **Architecture**: Client-server pattern, message protocols
6. **Testing**: Unit tests, integration tests, multi-client scenarios

## 📝 License

Dự án học thuật - Tự do sử dụng cho mục đích giáo dục.

---

**Tác giả**: AI Assistant  
**Ngày**: March 27, 2026  
**Ngôn ngữ**: Python 3.14