from django.core.management.base import BaseCommand
from api.models.project import Project
from api.models.team import Team
from api.models.team_user import TeamUser
from api.models.project_user import ProjectUser
from api.models.user import User
from api.models.enterprise import Enterprise
from api.models.task import Task
from api.models.report import Report
from api.models.document import Document
from api.models.notification import Notification
from api.models.comment import Comment
from api.models.chatroom import ChatRoom
from api.models.message import Message

from datetime import date


class Command(BaseCommand):
    help = 'Create sample data for the project'

    def handle(self, *args, **kwargs):
        # Tạo Enterprise mẫu
        enterprise = Enterprise.objects.create(
            Name="Tech Corp",
            Address="123 Tech St.",
            PhoneNumber="123-456-7890",
            Email="contact@techcorp.com",
            Industry="Technology"
        )

        # Danh sách người dùng mẫu
        users_data = [
            {
                "full_name": "Alice Johnson",
                "email": "admin123@gmail.com",
                "role": "Admin",
                "department": "Engineering",
                "gender": "Female",
                "birth_date": date(1990, 5, 21),
                "phone": "0901234567",
                "province": "Hà Nội",
                "district": "Ba Đình",
                "address": "123 Đường Láng",
                "position": "Giám đốc kỹ thuật",
            },
            {
                "full_name": "Bob Smith",
                "email": "bob112312@techcorp.com",
                "role": "Manage",
                "department": "Marketing",
                "gender": "Male",
                "birth_date": date(1988, 3, 14),
                "phone": "0912345678",
                "province": "TP.HCM",
                "district": "Quận 1",
                "address": "456 Nguyễn Huệ",
                "position": "Trưởng phòng Marketing",
            },
            {
                "full_name": "Charlie Brown",
                "email": "charli1333@techcorp.com",
                "role": "User",
                "department": "Sales",
                "gender": "Male",
                "birth_date": date(1995, 7, 10),
                "phone": "0934567890",
                "province": "Đà Nẵng",
                "district": "Hải Châu",
                "address": "789 Lê Duẩn",
                "position": "Nhân viên bán hàng",
            },
        ]

        created_users = []

        for data in users_data:
            user = User.objects.create(
                full_name=data["full_name"],
                email=data["email"],
                role=data["role"],
                department=data["department"],
                gender=data["gender"],
                birth_date=data["birth_date"],
                phone=data["phone"],
                province=data["province"],
                district=data["district"],
                address=data["address"],
                position=data["position"],
                enterprise=enterprise,
            )
            user.set_password("123456")
            user.save()
            created_users.append(user)

        user1, user2, user3 = created_users

        self.stdout.write(self.style.SUCCESS("✅ Tạo người dùng mẫu thành công!"))

        # Tạo Projects
        project1 = Project.objects.create(
            project_name="Project X",
            description="A new innovative product.",
            status="Ongoing",
            start_date="2025-01-01",
            end_date="2025-12-31",
            manager=user1,
        )

        project2 = Project.objects.create(
            project_name="Project Y",
            description="An exciting marketing campaign.",
            status="On Hold",
            start_date="2025-02-01",
            end_date="2025-06-30",
            manager=user2,
        )

        # Gán thành viên vào Project
        for project, members in [
            (project1, [(user1, "Manager"), (user2, "Member"), (user3, "Support")]),
            (project2, [(user2, "Manager"), (user1, "Member"), (user3, "Support")]),
        ]:
            for user, role in members:
                ProjectUser.objects.create(
                    project=project,
                    user=user,
                    role_in_project=role
                )

        # Teams
        team1 = Team.objects.create(team_name="Alpha Team", project=project1, leader=user1)
        team2 = Team.objects.create(team_name="Beta Team", project=project2, leader=user2)

        TeamUser.objects.create(team=team1, user=user1, role_in_team="Lead")
        TeamUser.objects.create(team=team1, user=user2, role_in_team="Member")
        TeamUser.objects.create(team=team2, user=user2, role_in_team="Lead")
        TeamUser.objects.create(team=team2, user=user3, role_in_team="Support")

        # Tasks
        task1 = Task.objects.create(
            task_name="Task 1 for Project X",
            description="First task for the project",
            status="Pending",
            deadline="2025-05-01",
            assignee=user1,
            project=project1
        )
        task2 = Task.objects.create(
            task_name="Task 2 for Project Y",
            description="Second task for the project",
            status="In Progress",
            deadline="2025-06-01",
            assignee=user2,
            project=project2
        )

        # Reports
        Report.objects.create(
            title="Report on Project X",
            content="Progress report for Project X",
            submitted_by=user1
        )
        Report.objects.create(
            title="Report on Project Y",
            content="Progress report for Project Y",
            submitted_by=user2
        )

        # Documents
        Document.objects.create(
            file_name="Project_X_Plan.pdf",
            file_type="PDF",
            uploaded_by=user1,
            related_project=project1
        )
        Document.objects.create(
            file_name="Project_Y_Plan.pdf",
            file_type="PDF",
            uploaded_by=user2,
            related_project=project2
        )

        # Notifications
        Notification.objects.create(message="Task assignment notification for Project X", sent_to=user1)
        Notification.objects.create(message="Task assignment notification for Project Y", sent_to=user2)

        # Comments
        Comment.objects.create(content="This is a comment on Task 1 for Project X", created_by=user1, related_task=task1)
        Comment.objects.create(content="This is a comment on Task 2 for Project Y", created_by=user2, related_task=task2)

        # ChatRooms
        chatroom1 = ChatRoom.objects.create(name="Project X Discussion", created_by=user1)
        chatroom2 = ChatRoom.objects.create(name="Project Y Discussion", created_by=user2)

        # Messages
        Message.objects.create(content="Message in Project X Chat", sent_by=user1, chatroom=chatroom1)
        Message.objects.create(content="Message in Project Y Chat", sent_by=user2, chatroom=chatroom2)

        self.stdout.write(self.style.SUCCESS("🎉 Dữ liệu mẫu đầy đủ đã được tạo thành công!"))
