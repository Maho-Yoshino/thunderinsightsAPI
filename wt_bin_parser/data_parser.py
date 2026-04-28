import struct
import sys
from app.wt_bin_parser.data_classes import BlockInfo, DataType, ParamInfo
from app.wt_bin_parser.utils import get_byte_gen, read_7bit_encoded_int, read_bytes, read_c_string
#from data_classes import BlockInfo, DataType, ParamInfo
#from utils import get_byte_gen, read_7bit_encoded_int, read_bytes, read_c_string


def parse_binary_data(bytes_data):

    main_data_gen = get_byte_gen(bytes_data)

    packet_type = next(main_data_gen)

    if packet_type != 1:
        print("Unsuported packet type!")
        quit()

    names_count = read_7bit_encoded_int(main_data_gen)

    if names_count <= 0:
        print("Corrupted data!")
        quit()

    # reading the size, but its unused
    read_7bit_encoded_int(main_data_gen)

    name_map = []
    for _ in range(0, names_count):
        name_map.append(read_c_string(main_data_gen))

    blocks_count = read_7bit_encoded_int(main_data_gen)
    param_count = read_7bit_encoded_int(main_data_gen)
    large_data_size = read_7bit_encoded_int(main_data_gen)
    large_data = read_bytes(large_data_size, main_data_gen)

    param_infos = []
    for _ in range(0, param_count):
        param_infos.append(parse_param_info(main_data_gen, name_map, large_data))

    block_infos = []
    for _ in range(0, blocks_count):
        block_infos.append(parse_block_info(main_data_gen, name_map))

    param_index = param_count - 1
    for i in range(blocks_count - 1, -1, -1):
        blocks_params_count = len(block_infos[i].param_info)
        blocks_block_count = len(block_infos[i].block_info)
        if blocks_params_count > 0:
            for j in range(blocks_params_count - 1, -1, -1):
                block_infos[i].param_info[j] = param_infos[param_index]
                param_index -= 1

        if blocks_block_count > 0:
            block_index = block_infos[i].block_offset
            for j in range(0, blocks_block_count):
                block_infos[i].block_info[j] = block_infos[block_index + j]

    root = (
        block_infos[0]
        if blocks_count > 0
        else (BlockInfo(param_infos) if param_count > 0 else None)
    )

    return to_dict(root)


def parse_block_info(main_data_gen, name_map):

    id = read_7bit_encoded_int(main_data_gen) - 1
    params_count = read_7bit_encoded_int(main_data_gen)
    blocks_count = read_7bit_encoded_int(main_data_gen)
    block_offset = read_7bit_encoded_int(main_data_gen) if blocks_count > 0 else 0
    name = get_string_value_tagged(name_map, id)
    return BlockInfo(id, name, block_offset, params_count, blocks_count)


def parse_param_info(main_data_gen, name_map, large_data):
    data = read_bytes(8, main_data_gen)

    id = data[0] | (data[1] << 8) | (data[2] << 16)
    data_type = DataType(data[3])
    index = data[4] | (data[5] << 8) | (data[6] << 16) | ((data[7] & 0x7F) << 24)
    name = get_string_value_tagged(name_map, id)

    match data_type:
        case DataType.Str:
            tagged = (data[7] >> 7) == 1
            value = get_string_value(name_map, large_data, index, tagged)

        case DataType.Int:
            value = struct.unpack("i", data[4:8])[0]

        case DataType.Bool:
            value = data[4] == 1

        case DataType.Float:
            value = round(struct.unpack("f", data[4:8])[0], 4)

        case DataType.Vec2:
            x = struct.unpack("i", large_data[index: index + 4])[0]
            y = struct.unpack("i", large_data[index + 4: index + 8])[0]
            value = [x, y]

        case _:
            print(f"Parsing {data_type} is unimplemented yet!")
            quit()

    return ParamInfo(id, name, data_type, value)


def get_string_value(name_map, large_data, index, tagged):
    if tagged:
        return get_string_value_tagged(name_map, index)

    large_data_gen = get_byte_gen(large_data[index:])
    return read_c_string(large_data_gen)


def get_string_value_tagged(name_map, index):
    if index < 0:
        return ""

    return name_map[index]


def to_dict(block):

    result = {}
    if block.param_info:
        for param in block.param_info:
            if param.name in result:
                if type(result[param.name]) == list:
                    result[param.name].append(param.value)
                else:
                    temp = [result[param.name]]
                    temp.append(param.value)
                    result[param.name] = temp
            else:
                result[param.name] = param.value

    if block.block_info:
        for block in block.block_info:
            if block.name in result:
                if type(result[block.name]) == list:
                    result[block.name].append(to_dict(block))
                else:
                    temp = [result[block.name]]
                    temp.append(to_dict(block))
                    result[block.name] = temp
            else:
                result[block.name] = to_dict(block)

    return result
