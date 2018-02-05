(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', function() {
    setup();
    generate();
  });

  u.prototype.removeAttr = function(attr) {
    this.each(function(el) {
      el.removeAttribute(attr);
    });
    return this;
  };

  function setup() {
    var submitButton = u('form#request-words > input[type="submit"]');

    u('form').ajax(function(err, res) {
      var output = u('#output').empty();
      try {
        if (err) {
          showError(output, res ? res.error : 'request failed');
        } else {
          showWords(output, res.words);
        }
      } finally {
        submitButton.removeAttr('disabled');
      }
    }, function(xhr) {
      submitButton.attr({ disabled: 'disabled' });
    });

    u('select[form="request-words"]').on('change', function() {
      generate();
    });
  }

  function generate() {
    u('form#request-words').trigger('submit');
  }

  function showError(output, err) {
    output.append('<span class="error label">Error</span>');
  }

  function showWords(output, words) {
    var para = u('<p>').addClass('word-list');
    output.append(para);

    words.sort(function(lhs, rhs) {
      return rhs.p - lhs.p;
    });

    words.forEach(function(word) {
      para.append(u('<span>').text(word.w + ' '));
    });
  }
})()
