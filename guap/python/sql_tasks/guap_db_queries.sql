-- =====================================================
-- SQL TASK 1: Data Validation & Integrity Checks
-- =====================================================

-- Проверка корректности оценок (только 2-5)
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN 'PASS: Все оценки в допустимом диапазоне'
        ELSE 'FAIL: Найдены некорректные оценки'
    END AS validation_result,
    COUNT(*) AS invalid_count
FROM grades 
WHERE grade < 2 OR grade > 5 OR grade IS NULL;

-- Проверка уникальности email (дубликаты)
SELECT 
    email,
    COUNT(*) AS duplicates
FROM students 
WHERE email IS NOT NULL 
GROUP BY email 
HAVING COUNT(*) > 1;

-- Проверка ссылочной целостности: оценки без студента
SELECT g.id, g.student_id
FROM grades g
LEFT JOIN students s ON g.student_id = s.id
WHERE s.id IS NULL;

-- Проверка ссылочной целостности: оценки без предмета
SELECT g.id, g.subject_id
FROM grades g
LEFT JOIN subjects sub ON g.subject_id = sub.id
WHERE sub.id IS NULL;

-- Проверка: студенты без оценок (могут быть проблемой)
SELECT s.id, s.full_name, s.group_name
FROM students s
LEFT JOIN grades g ON s.id = g.student_id
WHERE g.id IS NULL AND s.is_active = TRUE;

-- Проверка: предметы без оценок (неиспользуемые)
SELECT sub.id, sub.name
FROM subjects sub
LEFT JOIN grades g ON sub.id = g.subject_id
WHERE g.id IS NULL;

-- =====================================================
-- SQL TASK 2: Edge Cases & Boundary Values
-- =====================================================

-- Студенты с максимальным количеством оценок (возможные выбросы)
SELECT 
    s.id, 
    s.full_name, 
    COUNT(g.id) AS exam_count
FROM students s
JOIN grades g ON s.id = g.student_id
GROUP BY s.id, s.full_name
ORDER BY exam_count DESC
LIMIT 10;

-- Средний балл по предметам (выявление аномалий)
SELECT 
    sub.name,
    ROUND(AVG(g.grade), 2) AS avg_grade,
    COUNT(g.id) AS total_grades,
    MIN(g.grade) AS min_grade,
    MAX(g.grade) AS max_grade,
    CASE 
        WHEN ROUND(AVG(g.grade), 2) < 3.0 THEN 'LOW'
        WHEN ROUND(AVG(g.grade), 2) > 4.5 THEN 'HIGH'
        ELSE 'NORMAL'
    END AS status
FROM subjects sub
JOIN grades g ON sub.id = g.subject_id
GROUP BY sub.id, sub.name
ORDER BY avg_grade;

-- Распределение оценок по семестрам
SELECT 
    semester,
    grade,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY semester), 1) AS percentage
FROM grades
WHERE semester IS NOT NULL
GROUP BY semester, grade
ORDER BY semester, grade;

-- Пустые/нулевые значения в критических полях
SELECT 
    'students.full_name' AS table_field, COUNT(*) AS null_count
    FROM students WHERE full_name IS NULL OR full_name = ''
UNION ALL
SELECT 'students.email', COUNT(*) FROM students WHERE email IS NULL OR email = ''
UNION ALL
SELECT 'students.group_name', COUNT(*) FROM students WHERE group_name IS NULL OR group_name = ''
UNION ALL
SELECT 'grades.grade', COUNT(*) FROM grades WHERE grade IS NULL
UNION ALL
SELECT 'grades.student_id', COUNT(*) FROM grades WHERE student_id IS NULL
UNION ALL
SELECT 'grades.subject_id', COUNT(*) FROM grades WHERE subject_id IS NULL
UNION ALL
SELECT 'schedule.time_start', COUNT(*) FROM schedule WHERE time_start IS NULL
UNION ALL
SELECT 'schedule.room', COUNT(*) FROM schedule WHERE room IS NULL OR room = '';

-- =====================================================
-- SQL TASK 3: UI-to-DB Validation (Cross-Check)
-- =====================================================

-- Сравнение данных: ожидаемые студенты в UI vs БД
-- Для UI теста: проверить что группа Z3420 имеет 25 студентов
SELECT 
    'Z3420' AS group_name,
    COUNT(*) AS db_count,
    25 AS expected_ui_count,
    CASE 
        WHEN COUNT(*) = 25 THEN 'MATCH'
        ELSE 'MISMATCH'
    END AS status
FROM students 
WHERE group_name = 'Z3420' AND is_active = TRUE;

-- Проверка что активные студенты могут логиниться (email не пуст)
SELECT 
    s.id,
    s.full_name,
    s.email,
    CASE 
        WHEN s.email IS NOT NULL AND s.email != '' THEN 'CAN_LOGIN'
        ELSE 'CANNOT_LOGIN'
    END AS login_status
FROM students s
WHERE s.is_active = TRUE
LIMIT 20;

-- Сверка расписания: должно быть не более 8 пар в день
SELECT 
    weekday,
    COUNT(*) AS classes_count,
    CASE 
        WHEN COUNT(*) > 8 THEN 'OVERLOAD'
        ELSE 'OK'
    END AS status
FROM schedule
WHERE group_name = 'Z3420'
GROUP BY weekday
ORDER BY classes_count DESC;

-- Проверка: все ли предметы имеют department
SELECT 
    sub.id,
    sub.name,
    CASE 
        WHEN sub.department IS NULL OR sub.department = '' THEN 'MISSING_DEPT'
        ELSE 'OK'
    END AS dept_status
FROM subjects sub
ORDER BY dept_status;

-- =====================================================
-- SQL TASK 4: Business Logic Validation
-- =====================================================

-- Студенты с непроставленными оценками за последний семестр
SELECT 
    s.id,
    s.full_name,
    s.group_name,
    5 AS current_semester
FROM students s
WHERE s.is_active = TRUE
AND NOT EXISTS (
    SELECT 1 FROM grades g 
    WHERE g.student_id = s.id AND g.semester = 5
);

-- Преподаватели с нагрузкой (по числу предметов)
SELECT 
    sub.department,
    COUNT(DISTINCT sub.id) AS subjects_count
FROM subjects sub
JOIN schedule sch ON sub.id = sch.subject_id
GROUP BY sub.department
ORDER BY subjects_count DESC;

-- Анализ успеваемости по дням недели (может влиять на результаты)
SELECT 
    TO_CHAR(exam_date, 'Day') AS weekday,
    AVG(grade) AS avg_grade,
    COUNT(*) AS exam_count
FROM grades
WHERE exam_date IS NOT NULL
GROUP BY TO_CHAR(exam_date, 'Day')
ORDER BY avg_grade;

-- =====================================================
-- SQL TASK 5: Performance & Index Validation
-- =====================================================

-- Проверка наличия индексов для часто используемых полей
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('students', 'grades', 'schedule', 'subjects')
ORDER BY tablename;

-- Оценка cardinality для ключевых полей
SELECT 
    'students.group_name' AS field,
    COUNT(DISTINCT group_name) AS unique_values
FROM students
UNION ALL
SELECT 'grades.grade', COUNT(DISTINCT grade) FROM grades
UNION ALL
SELECT 'schedule.weekday', COUNT(DISTINCT weekday) FROM schedule
UNION ALL
SELECT 'schedule.room', COUNT(DISTINCT room) FROM schedule;

-- =====================================================
-- SQL TASK 6: Data Quality Reports
-- =====================================================

-- Итоговый отчет по качеству данных
SELECT 
    'Total students' AS metric, COUNT(*)::text AS value FROM students
UNION ALL
SELECT 'Active students', COUNT(*)::text FROM students WHERE is_active = TRUE
UNION ALL
SELECT 'Total subjects', COUNT(*)::text FROM subjects
UNION ALL
SELECT 'Total grades', COUNT(*)::text FROM grades
UNION ALL
SELECT 'Students with grades', 
    (SELECT COUNT(DISTINCT student_id)::text FROM grades)
UNION ALL
SELECT 'Avg grade overall', 
    ROUND(AVG(grade), 2)::text FROM grades;

-- Отчет по задолженностям (оценки = 2)
SELECT 
    sub.name AS subject,
    COUNT(g.id) AS debt_count,
    COUNT(DISTINCT g.student_id) AS students_with_debts
FROM grades g
JOIN subjects sub ON g.subject_id = sub.id
WHERE g.grade = 2
GROUP BY sub.id, sub.name
ORDER BY debt_count DESC;

-- =====================================================
-- SQL TASK 7: Test Data Cleanup & Fixtures
-- =====================================================

-- Создание тестового студента
INSERT INTO students (full_name, group_name, email, enrolled_at, is_active)
VALUES ('Test Student', 'Z9999', 'test@guap.ru', CURRENT_DATE, TRUE)
RETURNING id, full_name, email;

-- Очистка тестовых данных
DELETE FROM grades 
WHERE student_id IN (
    SELECT id FROM students WHERE email LIKE '%@test.guap.ru'
);
DELETE FROM students WHERE email LIKE '%@test.guap.ru';

-- Сброс последовательностей после очистки (для PostgreSQL)
-- ALTER SEQUENCE students_id_seq RESTART WITH 1;