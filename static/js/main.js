// Toastr konfiqurasiyası
toastr.options = {
    "closeButton": true,
    "progressBar": true,
    "positionClass": "toast-bottom-right",
    "timeOut": "3000"
};

// AJAX sorğular üçün CSRF token
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", $('[name=csrfmiddlewaretoken]').val());
        }
    }
});

// Cədvəl sıralama
$('.sortable').on('click', 'th', function() {
    const table = $(this).parents('table').eq(0);
    const rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()));
    this.asc = !this.asc;
    if (!this.asc) {
        rows.reverse();
    }
    for (let i = 0; i < rows.length; i++) {
        table.append(rows[i]);
    }
});

function comparer(index) {
    return function(a, b) {
        const valA = getCellValue(a, index);
        const valB = getCellValue(b, index);
        return $.isNumeric(valA) && $.isNumeric(valB) ?
            valA - valB : valA.toString().localeCompare(valB);
    };
}

function getCellValue(row, index) {
    return $(row).children('td').eq(index).text();
}

// Dinamik form validasiyası
$('form').on('submit', function() {
    const requiredFields = $(this).find('[required]');
    let isValid = true;
    
    requiredFields.each(function() {
        if (!$(this).val()) {
            isValid = false;
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    
    return isValid;
});

// Mobil cihazlar üçün responsive table scroll
$('.table-responsive').on('scroll', function() {
    $(this).find('thead').css('transform', 
        'translateY(' + this.scrollTop + 'px)');
}); 