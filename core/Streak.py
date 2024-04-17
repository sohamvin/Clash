from urllib.parse import quote
import random
# from huffman.codec import HuffmanCodec


def caesar_cipher(text, shift):
  """
  Encrypts a text using a Caesar cipher with a specific shift value.

  Args:
      text: The text to be encrypted.
      shift: The number of positions to shift the letters (positive for forward, negative for backward).

  Returns:
      The encrypted text.
  """
  result = ""
  for char in text:
    if char.isalpha():
      # Convert char to uppercase for easier handling
      c = ord(char.upper())
      # Handle wrapping around the alphabet
      new_c = (c - ord('A') + shift) % 26
      new_c += ord('A')
      # Convert back to lowercase if original char was lowercase
      result += chr(new_c) if char.islower() else chr(new_c + 32)
    else:
      result += char
  return result[::-1]


def function(ip_data_in_dicts):
    main_str = ""
    
    for obj in ip_data_in_dicts:
        main_str += str(obj["correct"]) + " "

    # Create a HuffmanCodec object from the input data
    # codec = HuffmanCodec.from_data(main_str)

    # Encode a new string
    # new_string = "python"
    # encoded_data = codec.encode(main_str)
    
    i = random.randint(1, 25)
    
    m = i + ord('A')
    
    m = chr(m)
    
    
    
    encoded_data = caesar_cipher(main_str, i)
    
    send = {
      "encoded_data": "Answer to your queries: " + encoded_data[::-1],
      "from_to": str(m) + " to " + "A"
    }
    # print("Encoded:", encoded_data)
    return send
    # # Decode the encoded data
    # decoded_data = codec.decode(encoded_data)
    # print("Decoded:", decoded_data)





