# Initial version from https://gist.github.com/skuroda/5105635
# Posted on SO: http://stackoverflow.com/questions/15260843

# Things still to do:
#   complete more
#   show matched line in status bar
#   highlight matched word in the view
#   only complete unique (maybe make this an option? could be annoying with complete more)

import sublime_plugin


last_initial_pos = None
last_word_at_ipos = None

last_search_pos = None


def complete_word(view, edit, do_previous):
    global last_initial_pos, last_word_at_ipos, last_search_pos

    initial_word_region = view.word(view.sel()[0])
    word = view.substr(initial_word_region)

    if (initial_word_region.a == last_initial_pos and last_word_at_ipos is not None and
            last_search_pos is not None):
        position = last_search_pos
        word = last_word_at_ipos
    else:
        if do_previous:
            position = initial_word_region.begin()
        else:
            position = initial_word_region.end()
        last_initial_pos = initial_word_region.a
        last_word_at_ipos = word

    position += -1 if do_previous else 1

    print("word: %s; position: %d" % (word, position))

    size_checked = 0
    while size_checked < 5000:
        compare_word_region = view.word(position)
        compare_word = view.substr(compare_word_region)

        match_found = False
        # Found a match; replace current word
        if compare_word.startswith(word):
            view.replace(edit, initial_word_region, compare_word)
            match_found = True

        if do_previous:
            position = compare_word_region.begin() - 1
        else:
            position = compare_word_region.end() + 1

        size_checked += compare_word_region.size()
        if match_found or position == -1 or position > view.size():
            break

    last_search_pos = position


#
class CompletePreviousWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        complete_word(self.view, edit, True)


class CompleteNextWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        complete_word(self.view, edit, False)
