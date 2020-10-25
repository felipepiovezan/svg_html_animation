class ParallelEventContainer:
    """A class that processes all events on each frame.

    The main `process_event` function calls `process_event` on all of the
    underlying events. It guarantees to its underlying events that elapsed time
    starts at 0.

    A ParallelEventContainer is "done" when all of its events are complete.
    """

    def __init__(self, events, out):
        """Constructs a ParallelEventContainer from a list of Events.

        `events` must be a list of objects whose JS representation has a
        `process_event` function taking a time `elapsed` argument and returning
        true if and only if the event is complete. Each event must additionally
        have a python member variable `js_name` representing the name of the
        object in JS.
        """

        self.js_name = ParallelEventContainer.gen_unique_name()
        list_str = ', '.join([f'{event.js_name}' for event in events])
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
        return 'parallel' + str(ParallelEventContainer.gid)
