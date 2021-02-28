WORDGEN = _venv/bin/python -m wordgen.cli

SIMPLE_SOURCES = \
  _data/eff_large_wordlist.txt

UNIVERSE_SOURCES = \
  _data/web2 \
  _data/eff_large_wordlist.txt

NAME_SOURCES = \
  _data/propernames \
  _data/usernames_sanitized.txt

ARTIFACTS = \
  _venv \
  _data \
  _init.ok \
  _model_simple.ok \
  _model_universe.ok \
  _model_name.ok \
  _model_name4G.ok \
  _model.ok


.PHONY: all clean

all: _model.ok
	@:

clean:
	rm -rf $(ARTIFACTS)

_init.ok:
	mkdir -p _data
	python3 -m venv _venv
	_venv/bin/pip install -r requirements.txt
	@touch $@

_model_simple.ok: _init.ok $(SIMPLE_SOURCES)
	cat $(SIMPLE_SOURCES) | $(WORDGEN) train --group Simple _data/models.h5
	@touch $@

_model_universe.ok: _init.ok $(UNIVERSE_SOURCES)
	cat $(UNIVERSE_SOURCES) | $(WORDGEN) train --group Universe _data/models.h5
	@touch $@

_model_name.ok: _init.ok $(NAME_SOURCES)
	cat $(NAME_SOURCES) | $(WORDGEN) train --group Name --token-size 3 _data/models.h5
	@touch $@

_model_name4G.ok: _init.ok $(NAME_SOURCES)
	cat $(NAME_SOURCES) | $(WORDGEN) train --group Name4G --token-size 4 _data/models.h5
	@touch $@

_model.ok: _model_simple.ok _model_universe.ok _model_name.ok _model_name4G.ok
	@touch $@

_data/usernames_sanitized.txt: _data/usernames.txt
	iconv -c -t ascii $< > $@ || :

_data/eff_large_wordlist.txt:
	curl -Lo $@ 'https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt'

_data/usernames.txt:
	curl -Lo $@ 'https://github.com/jeanphorn/wordlist/raw/master/usernames.txt'

_data/web2:
	curl -Lo $@ 'http://cvsweb.netbsd.org/bsdweb.cgi/~checkout~/src/share/dict/web2?rev=1.54'

_data/propernames:
	curl -Lo $@ 'http://cvsweb.netbsd.org/bsdweb.cgi/~checkout~/src/share/dict/propernames?rev=1.3.108.1'
