from dataclasses import dataclass
from typing import List


@dataclass
class Lesson:
    id: int
    cancelled: bool
    online: bool
    optional: bool
    start: int
    end: int
    start_timeslot_name: str
    end_timeslot_name: str
    subjects: List[str]
    groups: List[str]
    teachers: List[str]
    online_teachers: List[str]
    locations: List[str]
    planned_attendance: bool
    student_enrolled: bool

    def __str__(self) -> str:
        return f"{self.start_timeslot_name} - {', '.join(self.subjects)} - {', '.join(self.teachers)} - {', '.join(self.locations)}"

    @staticmethod
    def to_lesson(zermelo_lesson) -> "Lesson":
        l = zermelo_lesson
        id = l["id"]
        cancelled = l["cancelled"]
        online = l["online"]
        optional = l["optional"]
        start = l["start"]
        end = l["end"]
        start_timeslot_name = l["startTimeSlotName"]
        end_timeslot_name = l["endTimeSlotName"]
        subjects = l["subjects"]
        groups = l["groups"]
        teachers = l["teachers"]
        online_teachers = l["onlineTeachers"]
        locations = l["locations"]
        planned_attendance = None
        student_enrolled = None
        try:
            planned_attendance = l["plannedAttendance"]
            student_enrolled = l["studentEnrolled"]
        except KeyError:
            # Not an optional lesson
            pass
        return Lesson(id, cancelled, online, optional, start, end, start_timeslot_name, end_timeslot_name, subjects, groups, teachers, online_teachers, locations, planned_attendance, student_enrolled)
