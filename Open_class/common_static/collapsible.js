document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.collapsible');
    var instances = M.Collapsible.init(elems, {
      onOpenEnd: function (el) {
        $(el).find("i.fa-caret-down").removeClass('fa-caret-down').addClass('fa-caret-up');
        $(el).find("div.collapsible-header").addClass('teal-text');
      },
      onCloseEnd: function (el) {
        $(el).find("i.fa-caret-up").removeClass('fa-caret-up').addClass('fa-caret-down');
        $(el).find("div.collapsible-header").removeClass('teal-text');
      }
    });
  });