import sys
import time
import os
from datetime import datetime
from lettuce.terrain import after
from lettuce.terrain import before
from xml.dom import minidom

def wrt_output(filename, content):
    f = open(filename, "w")
    f.write(content.encode('utf-8'))
    f.close()

def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6


def enable(filename=None):

    doc = minidom.Document()
    root = doc.createElement("testResults")
    root.setAttribute('version', '1.2')
    doc.appendChild(root)
    start_time=datetime.now()
    output_filename = filename or "file.*.lettucetests.jmx"


    def cast_bool_to_ok_fail(is_ok):
        return "OK" if is_ok else "FAIL"

    def logitem(duration, timestamp, label, url, code, is_ok, size):
        log_string={
        't':str(duration),
        'ts':str(int(timestamp*1000)),
        'rc':str(code),
        'lb':str(label),
        'rm':cast_bool_to_ok_fail(is_ok),
        's': 'true' if  is_ok  else 'false', 
        'lt': '0',
        'tn': 'thread-0',
        'by': str(int(size)),
        'dt' : 'text',
        'url':str(url)
        }
        xml_string_element=doc.createElement("sample")
        for attr in log_string.keys():
            xml_string_element.setAttribute(attr, log_string[attr])
        root.appendChild(xml_string_element)

    @before.each_step
    def time_step(step):
        step.started = datetime.now()

    @after.each_step
    def report_event(step):
        duration=total_seconds((datetime.now() - step.started))
        timestamp=int(time.time())
        label=step.sentence
        url=str.format('{0}.{1}.{2}',step.scenario.feature.name, step.scenario.name, step.sentence)
        code=1
        is_ok=not step.failed
        code=0 if is_ok else 1
        size=0
        if step.ran:
            logitem(duration, timestamp, label, url, code, is_ok, size)

    @after.all
    def write_all(total):
        output_filename = filename or "file.*.lettucetests.jmx"
        pid=os.getpid()
        actual_filename=output_filename.replace('*', str(pid))
        fd=open(actual_filename, 'w')
        fd.write(doc.toprettyxml(indent="  "))
