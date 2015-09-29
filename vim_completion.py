# Initial version from https://gist.github.com/skuroda/5105635
# Posted on SO: http://stackoverflow.com/questions/15260843

# Things still to do:
#   complete more
#   only complete unique (maybe make this an option? could be annoying with complete more)
#   complete from other open buffers, MRU first

import sublime
import sublime_plugin

# The view that we searched in last
last_view = None

# The location of the beginning of the prefix that was last searched for
last_initial_pos = None

# The prefix that was at last_initial_pos last time we searched
last_word_at_ipos = None

# The place to begin searching for words on next complete_word
last_search_pos = None

# True iff the most recent search was in the 'previous' direction
last_search_was_previous = None

REGION_KEY = 'VimCompletion'
DRAW_FLAGS = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE

def complete_word(view, edit, do_previous):
    global last_initial_pos, last_word_at_ipos, last_search_pos, last_view, last_search_was_previous

    view.erase_regions(REGION_KEY)

    # Compute the region from the beginning of the word containing the cursor
    # through the cursor.
    initial_word_region = view.word(view.sel()[0])
    initial_word_region = sublime.Region(initial_word_region.a, view.sel()[0].a)
    word = view.substr(initial_word_region)

    if (last_view == view and initial_word_region.a == last_initial_pos and
            last_word_at_ipos is not None and
            word.startswith(last_word_at_ipos) and last_search_pos is not None):
        # Continue at previous search position with previous search prefix
        position = last_search_pos
        word = last_word_at_ipos

        if do_previous != last_search_was_previous:
            r = view.word(position + (1 if last_search_was_previous else -1))
            if do_previous:
                position = r.begin() - 1
            else:
                position = r.end() + 1
    else:
        # Start a new search
        if do_previous:
            position = initial_word_region.begin()
        else:
            position = initial_word_region.end()
        last_initial_pos = initial_word_region.a
        last_word_at_ipos = word
        last_view = view

    if (do_previous and position > 0) or (not do_previous and position < view.size()):
        position += -1 if do_previous else 1

    # sublime.status_message("word: %s; position: %d" % (word, position))

    match_found = False
    while not match_found and position >= 0 and position <= view.size():
        compare_word_region = view.word(position)
        compare_word = view.substr(compare_word_region)

        # If we find a word that starts with the proper prefix, it's a match!
        # But don't count it if we have just found our starting place.
        if compare_word.startswith(word) and compare_word_region.a != view.word(view.sel()[0]).a:
            # replace word
            view.replace(edit, initial_word_region, compare_word)
            view.add_regions(REGION_KEY, [compare_word_region], "error", "", DRAW_FLAGS)

            match_found = True

        if do_previous:
            position = compare_word_region.begin() - 1
        else:
            position = compare_word_region.end() + 1

    if match_found:
        sublime.status_message(
            "Completion line: %s" %
            view.substr(view.line(sublime.Region(compare_word_region.a, compare_word_region.a))))
    else:
        sublime.status_message("No completion found")

    last_search_pos = position
    last_search_was_previous = do_previous


class CompletePreviousWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        complete_word(self.view, edit, True)


class CompleteNextWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        complete_word(self.view, edit, False)


class CompleteMoreCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        pass
