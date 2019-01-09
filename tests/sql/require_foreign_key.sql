-- enable:RequireForeignKey
-- >>> {"line": 14, "column": 13, "message_id": "MissingPrimaryKey"}
--
--

CREATE TABLE doesnt_match_column_regex(foo_id_not_a_references int);

CREATE TABLE inline_fk(foo_id int REFERENCES foo(id));

CREATE TABLE inline_fk(foo_id int, FOREIGN KEY (foo_id) REFERENCES foo(pk));

CREATE TABLE missing_fk(foo_id int);

ALTER TABLE alter_table_with_fk ADD COLUMN foo_id int REFERENCES foo(pk);

ALTER TABLE alter_table_with_fk_later ADD COLUMN foo_id int;
ALTER TABLE alter_table_with_fk_later ADD FOREIGN KEY (foo_id) REFERENCES foo(pk);

ALTER TABLE alter_table_without_fk ADD COLUMN foo_id int;

/*
    ALTER TABLE
    [{'RawStmt': {'stmt': {'AlterTableStmt': {'cmds': [{'AlterTableCmd': {'behavior': 0,
        'def': {'ColumnDef': {'colname': 'bar',
          'constraints': [{'Constraint': {'contype': 8,
             'fk_del_action': 'a',
             'fk_matchtype': 's',
             'fk_upd_action': 'a',
             'initially_valid': True,
             'location': 35,
             'pk_attrs': [{'String': {'str': 'key'}}],
             'pktable': {'RangeVar': {'inh': True,
               'location': 46,
               'relname': 'fore',
               'relpersistence': 'p'}}}}],
          'is_local': True,
          'location': 27,
          'typeName': {'TypeName': {'location': 31,
            'names': [{'String': {'str': 'baz'}}],
            'typemod': -1}}}},
        'subtype': 0}}],
     'relation': {'RangeVar': {'inh': True,
       'location': 12,
       'relname': 'foo',
       'relpersistence': 'p'}},
     'relkind': 37}},
   'stmt_len': 55}}]
    */
