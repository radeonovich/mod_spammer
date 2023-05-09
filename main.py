import zipfile
import io
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('amount', type=int, default=1, help='how many mods to add')
args = parser.parse_args()


# load empty mod in memory
with open('mod000000000.jar', 'rb') as f:
    input_bytes = f.read()


def process_changes(changes):
    with zipfile.ZipFile(io.BytesIO(input_bytes), 'r') as input_zip:
        with input_zip.open('com/example/mod000000000/ExampleMod.class') as class_file:
            class_bytes = class_file.read()
        with input_zip.open('META-INF/mods.toml') as toml_file:
            toml_bytes = toml_file.read()
        for i, change in enumerate(changes):
            # create new archive
            mf = io.BytesIO()
            with zipfile.ZipFile(mf, 'w') as output_zip:
                for name in input_zip.namelist():
                    if name != 'com/example/mod000000000/ExampleMod.class' and name != 'META-INF/mods.toml':
                        output_zip.writestr(name, input_zip.read(name))

                    # create folder with unique name
                    if name == 'com/example/mod000000000':
                        output_zip.writestr('com/example/' + str(change).zfill(9) + '/', '')

                # change ExampleMod.class
                class_modified_bytes = bytearray(class_bytes)
                number = str(change).zfill(9).encode()
                class_modified_bytes[0x1c:0x25] = number
                class_modified_bytes[0x8f:0x98] = number
                class_modified_bytes[0x5e1:0x5ea] = number
                # change mods.toml
                toml_modified_bytes = bytearray(toml_bytes)
                toml_modified_bytes[0xc8:0xd1] = str(change).zfill(9).encode()

                # add mofidied files in archive
                output_zip.writestr('com/example/' + 'mod' + str(change).zfill(9) + '/ExampleMod.class', class_modified_bytes)
                output_zip.writestr('META-INF/mods.toml', toml_modified_bytes)

            # save new archive on the disk
            output_bytes = mf.getvalue()
            with open(f'mods/mod{str(change).zfill(9)}.jar', 'wb') as f:
                f.write(output_bytes)


# create multiple threads
num_threads = 4
changes_per_thread = args.amount // num_threads
threads = []
for i in range(num_threads):
    start = i * changes_per_thread
    end = (i + 1) * changes_per_thread if i < num_threads - 1 else args.amount
    changes = range(start, end)
    thread = threading.Thread(target=process_changes, args=(changes,))
    threads.append(thread)
    thread.start()

# wait for threads to finish
for thread in threads:
    thread.join()

