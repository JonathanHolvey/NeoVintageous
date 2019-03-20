# Copyright (C) 2018 The NeoVintageous Team (NeoVintageous).
#
# This file is part of NeoVintageous.
#
# NeoVintageous is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# NeoVintageous is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NeoVintageous.  If not, see <https://www.gnu.org/licenses/>.

from collections import OrderedDict

from NeoVintageous.nv.ex.tokens import TokenCommand


def _literal_route(state, name, forcable=False, **kwargs):
    command = TokenCommand(name, **kwargs)

    if forcable and state.match('!'):
        command.forced = True

    return command


def _create_map_route(state, name):
    command = TokenCommand(name)

    m = state.match(r'\s*(?P<lhs>.+?)\s+(?P<rhs>.+?)\s*$')
    if m:
        command.params.update(m.groupdict())

    return command


def _create_unmap_route(state, name):
    command = TokenCommand(name)
    command.params.update(state.expect_match(r'\s*(?P<lhs>.+?)\s*$').groupdict())

    return command


def _resolve(state, command, pattern):
    m = state.match(pattern)
    if m:
        command.params.update(m.groupdict())

    return command


def _ex_route_bfirst(state):
    return _literal_route(state, 'bfirst')


def _ex_route_blast(state):
    return _literal_route(state, 'blast')


def _ex_route_bnext(state):
    return _literal_route(state, 'bnext')


def _ex_route_bprevious(state):
    return _literal_route(state, 'bprevious')


def _ex_route_browse(state):
    return _literal_route(state, 'browse')


def _ex_route_buffers(state):
    return _literal_route(state, 'buffers')


def _ex_route_cd(state):
    command = _literal_route(state, 'cd', forcable=True)

    state.skip(' ')
    state.ignore()

    if state.match('-'):
        raise NotImplementedError('parameter not implemented')

    m = state.match(r'(?P<path>.+?)\s*$')
    if m:
        command.params.update(m.groupdict())

    return command


def _ex_route_close(state):
    return _literal_route(state, 'close', forcable=True)


def _ex_route_copy(state):
    command = TokenCommand('copy')
    command.addressable = True
    command.params = state.expect_match(r'\s*(?P<address>.+?)\s*$').groupdict()

    return command


def _ex_route_cquit(state):
    return _literal_route(state, 'cquit')


def _ex_route_delete(state):
    command = TokenCommand('delete')
    command.addressable = True

    params = {'register': '"', 'count': None}

    state.skip(' ')
    state.ignore()

    c = state.consume()
    if c == state.EOF:
        command.params = params

        return command

    state.backup()
    state.skip(' ')
    state.ignore()

    m = state.expect_match(r'(?P<register>[a-zA-Z0-9"])(?:\s+(?P<count>\d+))?\s*$')

    params.update(m.groupdict())
    if params['count']:
        raise NotImplementedError('parameter not implemented')

    command.params = params

    return command


def _ex_route_double_ampersand(state):
    command = TokenCommand('&&', target='double_ampersand')
    command.addressable = True

    params = {'flags': [], 'count': ''}

    m = state.match(r'\s*([cgr])*\s*(\d*)\s*$')

    params['flags'] = list(m.group(1)) if m.group(1) else []
    params['count'] = m.group(2) or ''

    state.expect_eof()

    command.params = params

    return command


def _ex_route_edit(state):
    command = TokenCommand('edit')

    params = {
        'file_name': None
    }

    c = state.consume()
    if c == state.EOF:
        command.params = params

        return command

    bang = c == '!'
    if not bang:
        state.backup()

    while True:
        c = state.consume()
        if c == state.EOF:
            command.params = params
            command.forced = bang

            return command

        if c in ('+', '#'):
            raise NotImplementedError('parameter not implemented')

        if c != ' ':
            state.match(r'.*')
            params['file_name'] = state.emit().strip()

            state.skip(' ')
            state.ignore()


def _ex_route_exit(state):
    return _literal_route(state, 'exit')


def _ex_route_file(state):
    return _literal_route(state, 'file')


def _ex_route_global(state):
    command = TokenCommand('global')
    command.addressable = True
    params = {}

    c = state.consume()

    bang = c == '!'
    sep = c if not bang else state.consume()

    if c not in '!:?/\\&$':
        raise ValueError('bad separator: ' + c)

    state.ignore()

    while True:
        c = state.consume()

        if c == state.EOF:
            raise ValueError('unexpected EOF in: ' + state.source)

        if c == sep:
            state.backup()

            params['pattern'] = state.emit()

            state.consume()
            state.ignore()
            break

    cmd = state.match(r'.*$').group(0).strip()
    if cmd:
        params['cmd'] = cmd

    command.params = params
    command.forced = bang

    return command


def _ex_route_help(state):
    command = TokenCommand('help')
    match = state.expect_match(r'(?P<bang>!)?\s*(?P<subject>.+)?$').groupdict()
    params = {'subject': match['subject']}
    bang = bool(match['bang'])

    command.params = params
    command.forced = bang

    return command


def _ex_route_let(state):
    command = TokenCommand('let')
    params = {'name': None, 'value': None}

    m = state.expect_match(
        r'(?P<name>.+?)\s*=\s*(?P<value>.+?)\s*$',
        on_error=lambda: Exception("E121: Undefined variable"))

    params.update(m.groupdict())

    command.params = params

    return command


def _ex_route_move(state):
    command = TokenCommand('move')
    command.addressable = True

    state.skip(' ')
    state.ignore()

    m = state.match(r'(?P<address>.*$)')
    if m:
        command.params['address'] = m.group(0).strip() or '.'

    return command


def _ex_route_new(state):
    return _literal_route(state, 'new')


def _ex_route_nnoremap(state):
    return _create_map_route(state, 'nnoremap')


def _ex_route_noremap(state):
    return _create_map_route(state, 'noremap')


def _ex_route_nunmap(state):
    return _create_unmap_route(state, 'nunmap')


def _ex_route_only(state):
    return _literal_route(state, 'only', forcable=True)


def _ex_route_onoremap(state):
    return _create_map_route(state, 'onoremap')


def _ex_route_ounmap(state):
    return _create_unmap_route(state, 'ounmap')


def _ex_route_print(state):
    command = TokenCommand('print')
    command.addressable = True
    command.cooperates_with_global = True

    while True:
        c = state.consume()

        state.skip(' ')
        state.ignore()

        if c == state.EOF:
            break

        c = state.consume()
        if c.isdigit():
            state.match(r'\d*')
            command.params['count'] = state.emit()
            continue

        state.backup()

        m = state.expect_match(r'[l#p]+')
        command.params['flags'] = list(m.group(0))
        state.ignore()
        state.expect_eof()
        break

    return command


def _ex_route_pwd(state):
    return _literal_route(state, 'pwd')


def _ex_route_qall(state):
    return _literal_route(state, 'qall', forcable=True)


def _ex_route_quit(state):
    return _literal_route(state, 'quit', forcable=True)


def _ex_route_read(state):
    command = TokenCommand('read')

    params = {}

    state.skip(' ')
    state.ignore()

    c = state.consume()

    if c == '+':
        raise NotImplementedError('parameter not implemented')

    elif c == '!':
        m = state.match(r'(?P<cmd>.+)')
        params.update(m.groupdict())

    else:
        state.backup()
        m = state.match(r'(?P<file_name>.+)$')
        params.update(m.groupdict())

    state.expect_eof()

    command.params = params

    return command


def _ex_route_registers(state):
    return _literal_route(state, 'registers')


def _ex_route_set(state):
    command = TokenCommand('set')
    params = {'option': None, 'value': None}

    state.skip(' ')
    state.ignore()

    m = state.expect_match(r'(?P<option>.+?)(?:[:=](?P<value>.+?))?$')
    params.update(m.groupdict())

    command.params = params

    return command


def _ex_route_setlocal(state):
    command = TokenCommand('setlocal')
    params = {'option': None, 'value': None}

    state.skip(' ')
    state.ignore()

    m = state.expect_match(r'(?P<option>.+?)(?:[:=](?P<value>.+?))?$')
    params.update(m.groupdict())

    command.params = params

    return command


def _ex_route_shell(state):
    return _literal_route(state, 'shell')


def _ex_route_shell_out(state):
    command = TokenCommand('!', target='shell_out')
    command.addressable = True
    params = {'cmd': None}

    m = state.expect_match(r'(?P<cmd>.+)$')
    params.update(m.groupdict())

    command.params = params

    return command


def _ex_route_snoremap(state):
    return _create_map_route(state, 'snoremap')


def _ex_route_sunmap(state):
    return _create_unmap_route(state, 'sunmap')


def _ex_route_sort(state):
    command = _literal_route(state, 'sort', addressable=True)

    _resolve(state, command, r'\s*(?P<options>[iu]+)')

    return command


def _ex_route_split(state):
    command = _literal_route(state, 'split')

    _resolve(state, command, r'\s+(?P<file>.+)')

    return command


def _ex_route_substitute(state):
    command = TokenCommand('substitute')
    command.addressable = True

    delim = state.consume()

    if delim == state.EOF:
        return command

    state.backup()
    delim = state.consume()
    params = {
        "pattern": None,
        "replacement": None,
        "count": 1,
        "flags": [],
    }

    while True:
        c = state.consume()

        if c == delim:
            state.start += 1
            state.backup()
            params['pattern'] = state.emit()
            state.consume()
            break

        if c == state.EOF:
            raise ValueError("bad command: {0}".format(state.source))

    while True:
        c = state.consume()
        if c == delim:
            state.start += 1
            state.backup()
            params['replacement'] = state.emit()
            state.consume()
            state.ignore()
            break

        if c == state.EOF:
            state.start += 1
            params['replacement'] = state.emit()
            state.consume()
            state.ignore()
            break

    if state.match(r'\s*[&cegiInp#lr]+'):
        params['flags'] = list(state.emit().strip())
        if '&' in params['flags'] and params['flags'][0] != '&':
            raise ValueError("bad command: {}".format(state.source))

    if state.peek(' '):
        state.skip(' ')
        state.ignore()
        if state.match(r'\d+'):
            params['count'] = int(state.emit())

    state.skip(' ')
    state.ignore()
    state.expect_eof()

    command.params = params

    return command


def _ex_route_tabclose(state):
    return _literal_route(state, 'tabclose', forcable=True)


def _ex_route_tabfirst(state):
    return _literal_route(state, 'tabfirst', forcable=True)


def _ex_route_tablast(state):
    return _literal_route(state, 'tablast', forcable=True)


def _ex_route_tabnext(state):
    return _literal_route(state, 'tabnext', forcable=True)


def _ex_route_tabonly(state):
    return _literal_route(state, 'tabonly', forcable=True)


def _ex_route_tabprevious(state):
    return _literal_route(state, 'tabprevious', forcable=True)


def _ex_route_unmap(state):
    return _create_unmap_route(state, 'unmap')


def _ex_route_unvsplit(state):
    return _literal_route(state, 'unvsplit')


def _ex_route_vnoremap(state):
    return _create_map_route(state, 'vnoremap')


def _ex_route_vsplit(state):
    command = _literal_route(state, 'vsplit')

    _resolve(state, command, r'\s+(?P<file>.+)')

    return command


def _ex_route_vunmap(state):
    return _create_unmap_route(state, 'vunmap')


def _ex_route_wall(state):
    return _literal_route(state, 'wall', forcable=True)


def _ex_route_wq(state):
    return _literal_route(state, 'wq', forcable=True)


def _ex_route_wqall(state):
    return _literal_route(state, 'wqall', addressable=True)


def _ex_route_write(state):
    command = TokenCommand('write')
    command.addressable = True

    params = {
        '++': '',
        'file_name': '',
        '>>': False,
        'cmd': '',
    }

    bang = state.consume()
    if bang == state.EOF:
        command.params = params

        return command

    if bang != '!':
        bang = False
        state.backup()

    state.skip(' ')
    state.ignore()

    plus_plus_translations = {
        'ff': 'fileformat',
        'bin': 'binary',
        'enc': 'fileencoding',
        'nobin': 'nobinary'
    }

    while True:
        c = state.consume()
        if c == state.EOF:
            break

        if c == '+':
            state.expect('+')
            state.ignore()
            # TODO: expect_match should work with emit()
            # https://vimhelp.appspot.com/editing.txt.html#[++opt]
            m = state.expect_match(
                r'(?:f(?:ile)?f(?:ormat)?|(?:file)?enc(?:oding)?|(?:no)?bin(?:ary)?|bad|edit)(?=\s|$)',
                lambda: Exception("E474: Invalid argument"))

            name = m.group(0)
            params['++'] = plus_plus_translations.get(name, name)
            state.ignore()
            continue

        if c == '>':
            state.expect('>')
            state.ignore()
            params['>>'] = True
            state.match(r'.*$')
            params['file_name'] = state.emit().strip()
            continue

        if c == '!':
            state.ignore()
            state.match(r'.*$')
            params['cmd'] = state.emit()
            continue

        if c != ' ':
            state.match(r'.*')
            params['file_name'] = state.emit().strip()
            state.skip(' ')
            state.ignore()

    command.params = params
    command.forced = bang == '!'

    return command


def _ex_route_yank(state):
    command = TokenCommand('yank')
    command.addressable = True

    params = {'register': '"', 'count': None}

    state.skip(' ')
    state.ignore()

    c = state.consume()
    if c == state.EOF:
        command.params = params

        return command

    state.backup()
    state.skip(' ')
    state.ignore()

    m = state.expect_match(r'(?P<register>[a-zA-Z0-9"])(?:\s+(?P<count>\d+))?\s*$')

    params.update(m.groupdict())
    if params['count']:
        raise NotImplementedError('parameter not implemented')

    command.params = params

    return command


# TODO: compile regexes. ??
ex_routes = OrderedDict()  # type: dict
ex_routes[r'!(?=.+)'] = _ex_route_shell_out
ex_routes[r'&&?'] = _ex_route_double_ampersand
ex_routes[r'(?:files|ls|buffers)!?'] = _ex_route_buffers
ex_routes[r'bf(?:irst)?'] = _ex_route_bfirst
ex_routes[r'bl(?:ast)?'] = _ex_route_blast
ex_routes[r'bn(?:ext)?'] = _ex_route_bnext
ex_routes[r'bN(?:ext)?'] = _ex_route_bprevious
ex_routes[r'bp(?:revious)?'] = _ex_route_bprevious
ex_routes[r'bro(?:wse)?'] = _ex_route_browse
ex_routes[r'br(?:ewind)?'] = _ex_route_bfirst
ex_routes[r'cd'] = _ex_route_cd
ex_routes[r'clo(?:se)?'] = _ex_route_close
ex_routes[r'co(?:py)?'] = _ex_route_copy
ex_routes[r'cq(?:uit)?'] = _ex_route_cquit
ex_routes[r'd(?:elete)?'] = _ex_route_delete
ex_routes[r'exi(?:t)?'] = _ex_route_exit
ex_routes[r'e(?:dit)?(?= |$)?'] = _ex_route_edit
ex_routes[r'f(?:ile)?'] = _ex_route_file
ex_routes[r'g(?:lobal)?'] = _ex_route_global
ex_routes[r'h(?:elp)?'] = _ex_route_help
ex_routes[r'let\s'] = _ex_route_let
ex_routes[r'm(?:ove)?(?=[^a]|$)'] = _ex_route_move
ex_routes[r'new'] = _ex_route_new
ex_routes[r'nn(?:oremap)?'] = _ex_route_nnoremap
ex_routes[r'no(?:remap)?'] = _ex_route_noremap
ex_routes[r'nun(?:map)?'] = _ex_route_nunmap
ex_routes[r'ono(?:remap)?'] = _ex_route_onoremap
ex_routes[r'on(?:ly)?'] = _ex_route_only
ex_routes[r'ou(nmap)?'] = _ex_route_ounmap
ex_routes[r'pw(?:d)?'] = _ex_route_pwd
ex_routes[r'p(?:rint)?'] = _ex_route_print
ex_routes[r'qa(?:ll)?'] = _ex_route_qall
ex_routes[r'q(?!a)(?:uit)?'] = _ex_route_quit
ex_routes[r'reg(?:isters)?'] = _ex_route_registers
ex_routes[r'r(?!eg)(?:ead)?'] = _ex_route_read
ex_routes[r'setl(?:ocal)?'] = _ex_route_setlocal
ex_routes[r'se(?:t)?(?=$|\s)'] = _ex_route_set
ex_routes[r's(?:ubstitute)?(?=[%&:/=]|$)'] = _ex_route_substitute
ex_routes[r'sh(?:ell)?'] = _ex_route_shell
ex_routes[r'snor(?:emap)?'] = _ex_route_snoremap
ex_routes[r'sor(?:t)?'] = _ex_route_sort
ex_routes[r'sp(?:lit)?'] = _ex_route_split
ex_routes[r'sunm(?:ap)?'] = _ex_route_sunmap
ex_routes[r'tabc(?:lose)?'] = _ex_route_tabclose
ex_routes[r'tabfir(?:st)?'] = _ex_route_tabfirst
ex_routes[r'tabl(?:ast)?'] = _ex_route_tablast
ex_routes[r'tabn(?:ext)?'] = _ex_route_tabnext
ex_routes[r'tabN(?:ext)?'] = _ex_route_tabprevious
ex_routes[r'tabo(?:nly)?'] = _ex_route_tabonly
ex_routes[r'tabp(?:revious)?'] = _ex_route_tabprevious
ex_routes[r'tabr(?:ewind)?'] = _ex_route_tabfirst
ex_routes[r'unm(?:ap)?'] = _ex_route_unmap
ex_routes[r'unvsplit'] = _ex_route_unvsplit
ex_routes[r'vn(?:oremap)?'] = _ex_route_vnoremap
ex_routes[r'vs(?:plit)?'] = _ex_route_vsplit
ex_routes[r'vu(?:nmap)?'] = _ex_route_vunmap
ex_routes[r'w(?:rite)?(?=(?:!?(?:\+\+|>>| |$)))'] = _ex_route_write
ex_routes[r'wa(?:ll)?'] = _ex_route_wall
ex_routes[r'wqa(?:ll)?'] = _ex_route_wqall
ex_routes[r'wq(?=[^a-zA-Z]|$)?'] = _ex_route_wq
ex_routes[r'xa(?:ll)?'] = _ex_route_wqall
ex_routes[r'x(?:it)?'] = _ex_route_exit
ex_routes[r'y(?:ank)?'] = _ex_route_yank
