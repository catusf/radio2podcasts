# Radio2Podcasts
Đọc thông tin từ các trang web có các chương trình radio và sách nói, và chuyển thành các podcast để nghe trên điện thoại dễ dàng.

## Giới thiệu
Ở Việt Nam, không nhiều trang web của các đài phát thanh cung cấp podcast để đọc giả nghe lại các chương trình. Dự án Radio2Podcasts này thực hiện việc
1. Chạy chương trình Python định kỳ (hàng giờ, hàng tuần...)
2. Tìm ra các file audio mới trên các website đó
3. Tạo ra file XML có format của một podcast
4. Tạo ra file HTML của tất cả các podcast vừa tạo ra
5. Lưu các file XML và HTML lên một trang web (hiện dùng GitHub Pages)

Từ đó người dùng mở file HTML là có thể đăng ký nghe podcast dùng các ứng dụng nghe podcast, ví dụ:
- Trên iOS: [Apple Podcasts](https://apps.apple.com/us/app/apple-podcasts/id525463029) hay [Pocket Casts](https://apps.apple.com/au/app/pocket-casts/id414834813)
- Trên Android: [Podcast Addict](https://play.google.com/store/apps/details?id=com.bambuna.podcastaddict&hl=en&gl=US) hay [Pocket Casts](https://play.google.com/store/apps/details?id=au.com.shiftyjelly.pocketcasts)

Các trang web hiện nay đã hỗ trợ:
- VOV1 http://vov1.vn/
- VOV2 http://vov2.vov.vn/
- VOV6 http://vov6.vov.vn/
- VOH https://radio.voh.com.vn/
- Phật pháp ứng dụng https://phatphapungdung.com/sach-noi/ (rất nhiều sách nói)

## Dành cho lập trình viên

Dự án này sử dụng Python, deploy trên GitHub Pages với các Actions được định nghĩa trước. Kết quả được giới thiệu [ở đây](https://catusf.github.io/).

### Credentials for email notifications
Khi chương trình gặp lỗi, email sẽ được gửi từ hòm thư **Gmail** được cấu hình dưới đây.:
- EMAIL_SENDER_ENV
- EMAIL_RECIPIENT_ENV
- EMAIL_PASSWORD_ENV


## Generate favicon from PNG
Uses [favicon.io](https://favicon.io/favicon-converter/)

Do vậy cần đặt các biến hệ thống trên máy phát triển và/hoặc trên GitHub [Secrets](https://github.com/catusf/radio2podcasts/settings/secrets). Mật khẩu Gmail dùng cho ứng dụng được tạo trên [Google Account](https://myaccount.google.com)  > Security > **App Passwords**.

<br>

[![Gitter](https://badges.gitter.im/radio2podcasts/community.svg)](https://gitter.im/radio2podcasts/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
