# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: inventory.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0finventory.proto\"\x88\x01\n\tInventory\x12\x14\n\x0cinventory_id\x18\x01 \x01(\x05\x12\x12\n\nproduct_id\x18\x02 \x01(\x05\x12\x0f\n\x07product\x18\x03 \x01(\t\x12\x16\n\x0estock_quantity\x18\x04 \x01(\x05\x12\x10\n\x08location\x18\x05 \x01(\t\x12\x16\n\x0elast_restocked\x18\x06 \x01(\t\"=\n\x0fInventoryUpdate\x12\x12\n\nproduct_id\x18\x01 \x01(\x05\x12\x16\n\x0estock_quantity\x18\x02 \x01(\x05\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'inventory_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _INVENTORY._serialized_start=20
  _INVENTORY._serialized_end=156
  _INVENTORYUPDATE._serialized_start=158
  _INVENTORYUPDATE._serialized_end=219
# @@protoc_insertion_point(module_scope)
