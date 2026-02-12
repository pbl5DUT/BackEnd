# BackEnd - Hệ Thống Quản Lý Dự Án

Backend API cho hệ thống quản lý dự án, nhiệm vụ và giao tiếp nhóm được xây dựng bằng Django REST Framework.

## 📋 Tổng Quan

Đây là backend API cho một hệ thống quản lý dự án toàn diện, cung cấp các chức năng:
- Quản lý người dùng và xác thực JWT
- Quản lý dự án và nhiệm vụ
- Chat realtime với WebSocket (Django Channels)
- Hệ thống thông báo
- Tích hợp Calendar và Google Calendar
- Báo cáo công việc
- Chatbot AI (GPT integration)

## 🛠️ Công Nghệ Sử Dụng

- **Framework**: Django 5.2.1
- **API**: Django REST Framework
- **Database**: MySQL (PyMySQL 1.1.1)
- **Authentication**: JWT (Simple JWT)
- **WebSocket**: Django Channels
- **Real-time Communication**: WebSocket cho chat
- **CORS**: django-cors-headers
