from hashlib import md5

CHUNK_SIZE = 99999

image_file = "test.jpg"
final_image_file = "test2.jpg"

list_chunks = []

with open(image_file, "rb") as infile:
    while True:
        chunk = infile.read(CHUNK_SIZE)

        if not chunk:
            break
        new_chunk_md5 = md5(chunk).hexdigest()
        list_chunks.append(new_chunk_md5)

        with open(new_chunk_md5, "wb") as file_to:
            file_to.write(chunk)

print(list_chunks)

ff = bytes()
for chk in list_chunks:
    with open(chk, "rb") as f:
        data = f.read(CHUNK_SIZE)
        ff += data

with open(final_image_file, "wb") as infile:
    infile.write(ff)
