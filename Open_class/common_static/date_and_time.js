document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.datepicker');
    var instances = M.Datepicker.init(elems, {
      format: "yyyy-mm-dd",
      i18n: {
        cancel: "取消",
        clear: "清除",
        done: "確認",
        months: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
        monthsShort: ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
        weekdays: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'],
        weekdaysShort: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'],
        weekdaysAbbrev: ['日', '一', '二', '三', '四', '五', '六'],
      }
    });
    var elems = document.querySelectorAll('.timepicker');
    var instances = M.Timepicker.init(elems, {
      twelveHour: false,
      i18n: {
        cancel: "取消",
        clear: "清除",
        done: "確認",
      }
    });
  });