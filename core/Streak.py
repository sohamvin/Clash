from urllib.parse import quote
# from huffman.codec import HuffmanCodec


def function(ip_data_in_dicts):
    main_str = ""

    for obj in ip_data_in_dicts:
        main_str += str(obj["question_md"]) + " "
        main_str += str(obj["correct"]) + " "

    # Create a HuffmanCodec object from the input data
    # codec = HuffmanCodec.from_data(main_str)

    # Encode a new string
    # new_string = "python"
    # encoded_data = codec.encode(main_str)
    encoded_data = quote(main_str)
    # print("Encoded:", encoded_data)
    return encoded_data
    # # Decode the encoded data
    # decoded_data = codec.decode(encoded_data)
    # print("Decoded:", decoded_data)





