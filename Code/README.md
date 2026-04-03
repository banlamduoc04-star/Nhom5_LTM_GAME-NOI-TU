
Word Chain Game - Game nối từ tiếng Việt

Một trò chơi nối từ đa người chơi sử dụng kiến trúc client-server TCP với giao diện desktop GUI.

Mục tiêu

Dự án nhằm áp dụng các khái niệm mạng máy tính cơ bản:

Giao tiếp socket TCP
Xử lý kết nối đa client
Truyền tải dữ liệu thời gian thực
Xác thực dữ liệu phía server
Luật chơi
Mỗi người chơi nhập một từ tiếng Việt.
Từ tiếp theo phải bắt đầu bằng chữ cái cuối của từ trước đó.
Từ nhập phải tồn tại trong từ điển tiếng Việt.
Server kiểm tra tính hợp lệ và gửi kết quả đến tất cả người chơi.

Ví dụ chuỗi hợp lệ:

a → an → ng → ga → an
Kiến trúc hệ thống
┌─────────────┐    TCP Socket    ┌─────────────┐
│   Client 1  │◄────────────────►│             │
│   (Tkinter) │                  │   Server    │
└─────────────┘                  │ (Threading) │
                                 └─────────────┘
┌─────────────┐                  ┌─────────────┐
│   Client 2  │◄────────────────►│ Dictionary  │
│   (Tkinter) │                  │ Validation  │
└─────────────┘                  └─────────────┘
Server (word_chain_server.py)
TCP Socket Server chấp nhận nhiều client đồng thời
Mô hình Thread-per-Client
Đảm bảo thread-safe bằng threading.Lock()
Kiểm tra quy tắc nối từ và từ điển
Broadcast thông tin tới tất cả client
Client (word_chain_client.py)
Giao diện desktop xây dựng bằng Tkinter
Network I/O chạy trong thread riêng để không làm treo GUI
Sử dụng Queue để trao đổi dữ liệu giữa network thread và GUI thread
Cập nhật trạng thái trò chơi theo thời gian thực
Validation (word_validation.py)
Xử lý Unicode tiếng Việt bằng NFC normalization
Kiểm tra quy tắc nối từ
Tra cứu từ điển với độ phức tạp O(1) bằng cấu trúc set
Cấu trúc thư mục
word-chain-game/
├── word_chain_server.py
├── word_chain_client.py
├── word_validation.py
├── vietnamese_dictionary.txt
├── README.md
└── test_*.py
Cách chạy chương trình
Bước 1: Khởi động Server
python word_chain_server.py

Server chạy trên địa chỉ localhost:5000 và tải từ điển.

Bước 2: Khởi động Client

Mở terminal mới:

python word_chain_client.py
Bước 3: Chơi game
Nhập tên người chơi
Nhập từ tiếng Việt theo quy tắc nối từ
Quan sát tin nhắn được broadcast từ server
