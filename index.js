(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', function() {
    setup();
    generate();
  });

  function setup() {
    var form = document.getElementById('request-words');
    var output = document.getElementById('output');
    var select = document.querySelector('select[form="request-words"]');

    ajax(form, function(err, res) {
      empty(output);

      if (res) {
        res = JSON.parse(res);
      }

      if (err) {
        showError(output, res ? res.error : 'request failed');
      } else {
        showWords(output, res.words);
      }
    });

    select.addEventListener('change', function(e) {
      generate();
    });
  }

  function generate() {
    var form = document.getElementById('request-words');
    form.dispatchEvent(new CustomEvent('submit'));
  }

  function showError(output, err) {
    output.appendChild(element('span', 'error label', String(err)));
  }

  function showWords(output, words) {
    var frag = document.createDocumentFragment();

    // Make words with higher likelihood come first.
    words.sort(function(lhs, rhs) {
      return rhs.p - lhs.p;
    });

    words.forEach(function(word) {
      frag.appendChild(element('span', 'word', word.w + ' '));
    });

    output.appendChild(frag);
  }

  // Create an element with specified class and text content.
  function element(name, cls, text) {
    var el = document.createElement(name);

    if (cls) {
      el.className = cls;
    }

    if (text) {
      el.appendChild(document.createTextNode(text));
    }

    return el;
  }

  // Remove all children nodes.
  function empty(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  // Change form to fire an AJAX when the submit button is pressed.
  function ajax(form, cb) {
    var button = form.querySelector('input[type="submit"]');

    form.addEventListener('submit', function(e) {
      e.preventDefault();

      var request = new XMLHttpRequest();

      var callback = function(err, res) {
        try {
          cb(err, res);
        } finally {
          button.removeAttribute('disabled');
        }
      };

      var handleStart = function(e) {
        button.setAttribute('disabled', 'disabled');
      };

      var handleError = function(e) {
        callback(new Error("request failed"), null);
      };

      var handleLoad = function(e) {
        var err = /^[45]/.test(request.status) && new Error(request.statusText);
        callback(err, request.response);
      };

      request.addEventListener('loadstart', handleStart);
      request.addEventListener('error', handleError);
      request.addEventListener('timeout', handleError);
      request.addEventListener('abort', handleError);
      request.addEventListener('load', handleLoad);

      request.open(form.method, form.action);
      request.send(new FormData(form));
    });
  }
})()
