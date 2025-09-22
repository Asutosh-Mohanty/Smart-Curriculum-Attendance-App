from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100)
    degree = models.ForeignKey('admins.Degree', on_delete=models.CASCADE, related_name='branches', null=True, blank=True)

    def __str__(self):
        if self.degree_id:
            return f"{self.name} ({self.degree.name})"
        return self.name


class Degree(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Group(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ("branch", "degree", "name")

    def __str__(self):
        return f"{self.name} - {self.branch.name} ({self.degree.name})"


# Note: Subject model is already defined in teachers app
# We'll use teachers.Subject instead of creating a duplicate

class GroupSubjectAssignment(models.Model):
    group = models.ForeignKey('admins.Group', on_delete=models.CASCADE, related_name='subject_assignments')
    subject = models.ForeignKey('teachers.Subject', on_delete=models.CASCADE, related_name='group_assignments')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='group_subject_assignments')

    class Meta:
        unique_together = ("group", "subject")

    def __str__(self):
        return f"{self.group.name}: {self.subject.name} -> {self.teacher.user.get_full_name()}"
