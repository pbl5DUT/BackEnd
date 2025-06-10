# api/serializers/work_report_serializers.py
from rest_framework import serializers
from api.models.user import User
from api.models.project import Project
from api.models.task import Task
from api.models.work_report import WorkReport
from api.serializers.user_serializer import UserSerializer
from api.serializers.project_serializer import ProjectSerializer


class WorkReportSerializer(serializers.ModelSerializer):
    # Hiển thị thông tin đầy đủ khi read
    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    tasks = serializers.SerializerMethodField()
    
    # Hỗ trợ NHIỀU CÁCH INPUT - Flexible!
    # Cách 1: Dùng ID fields (khuyến nghị)
    user_id = serializers.CharField(write_only=True, required=False)
    project_id = serializers.CharField(write_only=True, required=False)
    task_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = WorkReport
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def get_tasks(self, obj):
        """Lấy danh sách tasks với thông tin đầy đủ"""
        try:
            from api.serializers.task_serializer import TaskSerializer
        except ImportError:
            class SimpleTaskSerializer(serializers.ModelSerializer):
                class Meta:
                    model = Task
                    fields = '__all__'
            TaskSerializer = SimpleTaskSerializer
        
        tasks = obj.tasks.all()
        return TaskSerializer(tasks, many=True).data

    def to_internal_value(self, data):
        """
        🔥 KEY FIX: Chuyển đổi input format để hỗ trợ nhiều cách gửi data
        """
        # Tạo bản copy để không modify original data
        processed_data = data.copy()
        
        print(f"=== PROCESSING INPUT DATA ===")
        print(f"Original data: {data}")
        
        # 1. Xử lý USER input
        # Hỗ trợ cả "user": "user-2" và "user_id": "user-2"
        if 'user' in processed_data and processed_data['user']:
            user_value = processed_data.pop('user')
            if not processed_data.get('user_id'):
                processed_data['user_id'] = user_value
                print(f"✓ Converted user -> user_id: {user_value}")
        
        # 2. Xử lý PROJECT input  
        # Hỗ trợ cả "project": "prj-10" và "project_id": "prj-10"
        if 'project' in processed_data and processed_data['project']:
            project_value = processed_data.pop('project')
            if not processed_data.get('project_id'):
                processed_data['project_id'] = project_value
                print(f"✓ Converted project -> project_id: {project_value}")
        
        # 3. Xử lý TASKS input
        # Hỗ trợ cả "tasks": ["task-1"] và "task_ids": ["task-1"]
        if 'tasks' in processed_data and processed_data['tasks']:
            tasks_value = processed_data.pop('tasks')
            if not processed_data.get('task_ids'):
                # Đảm bảo tasks_value là list
                if isinstance(tasks_value, str):
                    tasks_value = [tasks_value]
                elif not isinstance(tasks_value, list):
                    tasks_value = list(tasks_value) if tasks_value else []
                    
                processed_data['task_ids'] = tasks_value
                print(f"✓ Converted tasks -> task_ids: {tasks_value}")
        
        print(f"Processed data: {processed_data}")
        print(f"=== END PROCESSING ===")
        
        # Gọi parent method với data đã được xử lý
        return super().to_internal_value(processed_data)

    def create(self, validated_data):
        """Tạo work report mới với debug chi tiết"""
        print(f"=== CREATING WORK REPORT ===")
        print(f"Validated data: {validated_data}")
        
        # 1. Xử lý user_id
        user_id = validated_data.pop('user_id', None)
        user_instance = None
        if user_id:
            try:
                user_instance = User.objects.get(user_id=user_id)
                validated_data['user'] = user_instance
                print(f"✓ User found: {user_instance.user_id} - {getattr(user_instance, 'full_name', 'N/A')}")
            except User.DoesNotExist:
                print(f"✗ User not found: {user_id}")
                raise serializers.ValidationError({
                    'user_id': f'User với ID "{user_id}" không tồn tại'
                })

        # 2. Xử lý project_id
        project_id = validated_data.pop('project_id', None)
        project_instance = None
        if project_id:
            try:
                project_instance = Project.objects.get(project_id=project_id)
                validated_data['project'] = project_instance
                print(f"✓ Project found: {project_instance.project_id} - {project_instance.project_name}")
            except Project.DoesNotExist:
                print(f"✗ Project not found: {project_id}")
                raise serializers.ValidationError({
                    'project_id': f'Project với ID "{project_id}" không tồn tại'
                })

        # 3. Xử lý task_ids
        task_ids = validated_data.pop('task_ids', None)
        tasks_to_add = []
        if task_ids:
            print(f"Processing tasks: {task_ids}")
            for task_id in task_ids:
                try:
                    task = Task.objects.get(task_id=task_id)
                    tasks_to_add.append(task)
                    print(f"✓ Task found: {task.task_id} - {getattr(task, 'task_name', 'N/A')}")
                except Task.DoesNotExist:
                    print(f"✗ Task not found: {task_id}")
                    raise serializers.ValidationError({
                        'task_ids': f'Task với ID "{task_id}" không tồn tại'
                    })

        # 4. Tạo ID tự động nếu không có
        if 'id' not in validated_data or not validated_data['id']:
            import uuid
            validated_data['id'] = f"WR_{uuid.uuid4().hex[:8].upper()}"
            print(f"✓ Generated ID: {validated_data['id']}")

        # 5. Tạo work report
        print(f"Creating WorkReport with data: {validated_data}")
        work_report = WorkReport.objects.create(**validated_data)
        print(f"✓ WorkReport created: {work_report.id}")

        # 6. Thêm tasks nếu có
        if tasks_to_add:
            work_report.tasks.set(tasks_to_add)
            print(f"✓ Added {len(tasks_to_add)} tasks to work report")

        print(f"=== WORK REPORT CREATION COMPLETED ===")
        return work_report

    def update(self, instance, validated_data):
        """Cập nhật work report với debug chi tiết"""
        print(f"=== UPDATING WORK REPORT ===")
        print(f"Instance ID: {instance.id}")
        print(f"Validated data: {validated_data}")
        
        # 1. Xử lý user_id
        user_id = validated_data.pop('user_id', None)
        if user_id:
            try:
                instance.user = User.objects.get(user_id=user_id)
                print(f"✓ Updated user: {instance.user.user_id}")
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'user_id': f'User với ID "{user_id}" không tồn tại'
                })

        # 2. Xử lý project_id
        project_id = validated_data.pop('project_id', None)
        if project_id:
            try:
                instance.project = Project.objects.get(project_id=project_id)
                print(f"✓ Updated project: {instance.project.project_id}")
            except Project.DoesNotExist:
                raise serializers.ValidationError({
                    'project_id': f'Project với ID "{project_id}" không tồn tại'
                })

        # 3. Xử lý task_ids
        task_ids = validated_data.pop('task_ids', None)
        if task_ids is not None:
            tasks = []
            for task_id in task_ids:
                try:
                    task = Task.objects.get(task_id=task_id)
                    tasks.append(task)
                    print(f"✓ Task found for update: {task.task_id}")
                except Task.DoesNotExist:
                    raise serializers.ValidationError({
                        'task_ids': f'Task với ID "{task_id}" không tồn tại'
                    })
            instance.tasks.set(tasks)
            print(f"✓ Updated {len(tasks)} tasks")

        # 4. Cập nhật các trường khác
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            print(f"✓ Updated {attr}: {value}")

        instance.save()
        print(f"✓ WorkReport updated successfully")
        return instance

    def to_representation(self, instance):
        """Tùy chỉnh output representation"""
        data = super().to_representation(instance)
        
        request = self.context.get('request')
        
        # Query parameters để control output
        if request and request.query_params.get('include_tasks') == 'false':
            data.pop('tasks', None)
            
        if request and request.query_params.get('include_user_details') == 'false':
            if 'user' in data and data['user']:
                data['user'] = {'user_id': data['user']['user_id']}
                
        if request and request.query_params.get('include_project_details') == 'false':
            if 'project' in data and data['project']:
                data['project'] = {'project_id': data['project']['project_id']}

        return data


class WorkReportListSerializer(WorkReportSerializer):
    """Serializer tối ưu cho list view"""
    project = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    
    class Meta(WorkReportSerializer.Meta):
        pass

    def get_project(self, obj):
        """Chỉ trả về thông tin cơ bản của project"""
        if obj.project:
            return {
                'project_id': obj.project.project_id,
                'project_name': obj.project.project_name,
                'status': obj.project.status
            }
        return None

    def get_user(self, obj):
        """Chỉ trả về thông tin cơ bản của user"""
        if obj.user:
            return {
                'user_id': obj.user.user_id,
                'username': getattr(obj.user, 'username', ''),
                'full_name': getattr(obj.user, 'full_name', '')
            }
        return None

    def get_tasks(self, obj):
        """Chỉ trả về thông tin cơ bản của tasks trong list view"""
        tasks = obj.tasks.all()
        return [
            {
                'task_id': task.task_id,
                'task_name': getattr(task, 'task_name', ''),
                'status': getattr(task, 'status', '')
            }
            for task in tasks
        ]


class WorkReportDetailSerializer(WorkReportSerializer):
    """Serializer đầy đủ cho detail view"""
    pass