import sqlite3

class sql:
    def execute(banco=None, retorno=False, command=None, insert_values=None):
        if not retorno:
            if banco and command:
                try:
                    conn = sqlite3.connect(f"{banco}")
                    with conn:
                        if insert_values:
                            conn.cursor().execute(f"{command}", insert_values)
                        else:
                            conn.cursor().execute(f"{command}")
                    conn.close()
                except (Exception, IOError, EOFError, OSError, OverflowError) as erro:
                    # print(str(erro))
                    return str(erro)
        else:
            if command:
                try:
                    conn = sqlite3.connect(f"{banco}")
                    with conn:
                        if insert_values:
                            result = conn.cursor().execute(f"""{command}""", insert_values)
                        else:
                            result = conn.cursor().execute(f"""{command}""")
                        result_select = [i for i in result]
                    conn.close()
                    return result_select
                except (Exception, IOError, EOFError, OSError, OverflowError) as erro:
                    # print(str(erro))
                    return str(erro)
