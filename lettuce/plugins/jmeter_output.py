import time
import os
from datetime import datetime

from lettuce.terrain import after
from lettuce.terrain import before
from xml.dom import minidom

def wrt_output(filename, content):
    with open(filename, "w+") as f:
        f.write(content.encode('utf-8'))

def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6

def enable(filename=None):
    doc = minidom.Document()
    root = doc.createElement("testResults")
    root.setAttribute('version', '1.2')
    doc.appendChild(root)

    def cast_bool_to_ok_fail(is_ok):
        return "OK" if is_ok else "FAIL"

    def logitem(duration, timestamp, label, url, code, is_ok, size):
        log_string={
        't':str(int(duration*1000)),
        'ts':str(int(timestamp*1000)),
        'rc':str(code),
        'lb':str(label),
        'rm':cast_bool_to_ok_fail(is_ok),
        's': 'True' if  is_ok  else 'False', 
        'lt': '0',
        'tn': 'thread-0',
        'by': str(int(size)),
        'dt' : 'text',
        'url':str(url)
        }
        xml_string_element=doc.createElement('sample')
        for attr in log_string.keys():
            xml_string_element.setAttribute(attr, log_string[attr])
        root.appendChild(xml_string_element)

    @before.each_step
    def time_step(step):
        step.started = datetime.now()

    @after.each_step
    def report_event(step):
        if getattr(step, 'started', None):
            duration=total_seconds((datetime.now() - step.started))
            timestamp = time.mktime(step.started.timetuple())
        else:
            duration = 0
            timestamp = 0
        
        label = step.sentence
        url = str.format('{0}.{1}.{2}', step.scenario.feature.name, 
                         step.scenario.name, step.sentence)
        is_ok = not step.failed
        code= 0 if is_ok else 1
        size= 0
        if step.ran:
            logitem(duration, timestamp, label, url, code, is_ok, size)

    @after.all
    def write_all(total):
        output_filename = filename or "file.*.lettucetests.jmx"
        pid=os.getpid()
        actual_filename=output_filename.replace('*', str(pid))

        with open(actual_filename, 'w+') as fd:
            fd.write(doc.toprettyxml(indent="  "))
