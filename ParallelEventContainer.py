class ParallelEventContainer:
    """ A class that advances all events on each frame.

    This class contains a list of events that are all advanced on each frame.
    The main `process_event` function calls `process_event` on all of the
    underlying events with the same elapsed time. It guarantees to its
    underlying events that elapsed time starts at 0. It returns true when all
    events have finished.
    """

    def __init__(self, events, out):
        """Construct a ParallelEventContainer from a list of Events."""

        self.js_name = ParallelEventContainer.gen_unique_name()
        list_str = ', '.join([f'{event.js_name}' for event in self.events])
        print(
            f'let {self.js_name} = new ParallelEventContainer([{list_str}])',
            file=out)

    def print_js_class(out):
        print(f'''
            class ParallelEventContainer {{
              constructor(events) {{
                this.events = events;
                this.base_elapsed = undefined;
              }}

              process_event(elapsed) {{
                if (this.base_elapsed === undefined)
                  this.base_elapsed = elapsed;

                event_elapsed = elapsed - this.base_elapsed;
                finished = true;

                this.events.forEach(function(event) {{
                  finished &&= event.process_event(event_elapsed);
                }});

                if (finished)
                  base_elapsed = undefined;
                return finished;
              }}
            }}''', file=out)

    gid = -1

    def gen_unique_name():
        ParallelEventContainer.gid += 1
        return 'parallel' + str(SvgJsGroup.gid)
