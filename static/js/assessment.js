class AssessmentManager {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Qiymət dəyişikliyi
        $(document).on('change', '.grade-cell input', (e) => {
            const input = $(e.target);
            const studentId = input.data('student');
            const typeId = input.data('type');
            const value = input.val();
            
            this.saveGrade(studentId, typeId, value);
        });

        // Qiymət validasiyası
        $(document).on('input', '.grade-cell input', (e) => {
            const input = $(e.target);
            const minGrade = parseFloat(input.data('min'));
            const maxGrade = parseFloat(input.data('max'));
            let value = parseFloat(input.val());

            if (value < minGrade) value = minGrade;
            if (value > maxGrade) value = maxGrade;

            input.val(value);
        });
    }

    saveGrade(studentId, typeId, value) {
        $.ajax({
            url: '/assessments/api/save-grade/',
            method: 'POST',
            data: {
                student_id: studentId,
                type_id: typeId,
                grade: value,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: (response) => {
                if (response.success) {
                    toastr.success('Qiymət yadda saxlanıldı');
                } else {
                    toastr.error(response.error);
                }
            },
            error: () => {
                toastr.error('Xəta baş verdi');
            }
        });
    }
} 