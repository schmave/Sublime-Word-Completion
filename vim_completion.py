# Initial version from https://gist.github.com/skuroda/5105635
# Posted on SO: http://stackoverflow.com/questions/15260843

# Things still to do:
#   complete more
#   highlight matched word in the view
#   only complete unique (maybe make this an option? could be annoying with complete more)

import sublime
import sublime_plugin


last_initial_pos = None
last_word_at_ipos = None

last_search_pos = None


def complete_word(view, edit, do_previous):
    global last_initial_pos, last_word_at_ipos, last_search_pos

    # Compute the region from the beginning of the word containing the cursor
    # through the cursor.
    initial_word_region = view.word(view.sel()[0])
    initial_word_region = sublime.Region(initial_word_region.a, view.sel()[0].a)
    word = view.substr(initial_word_region)

    if (initial_word_region.a == last_initial_pos and last_word_at_ipos is not None and
            word.startswith(last_word_at_ipos) and last_search_pos is not None):
        position = last_search_pos
        word = last_word_at_ipos
    else:
        if do_previous:
            position = initial_word_region.begin()
        else:
            position = initial_word_region.end()
        last_initial_pos = initial_word_region.a
        last_word_at_ipos = word

    if (do_previous and position > 0) or (not do_previous and position < view.size()):
        position += -1 if do_previous else 1

    # sublime.status_message("word: %s; position: %d" % (word, position))

    size_checked = 0
    match_found = False
    while (size_checked < 5000 and not match_found and position >= 0 and
           position <= view.size()):
        compare_word_region = view.word(position)
        compare_word = view.substr(compare_word_region)

        # If we find a word that starts with the proper prefix, it's a match!
        # But don't count it if we have just found our starting place.
        if compare_word.startswith(word) and compare_word_region.a != view.word(view.sel()[0]).a:
            # replace word
            view.replace(edit, initial_word_region, compare_word)
            match_found = True

        if do_previous:
            position = compare_word_region.begin() - 1
        else:
            position = compare_word_region.end() + 1

        size_checked += compare_word_region.size()

    if match_found:
        sublime.status_message(
            "Completion line: %s" %
            view.substr(view.line(sublime.Region(position, position))))
    else:
        sublime.status_message("No completion found")

    last_search_pos = position


#
class CompletePreviousWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        complete_word(self.view, edit, True)


class CompleteNextWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        complete_word(self.view, edit, False)
