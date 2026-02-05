import docker
import os
import logging

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

path = os.path.dirname(os.path.abspath(__file__))

print("Contenedores:", [c.name for c in client.containers.list(all=True)])
print("Imágenes:", client.images.list())


def build_image():
    global path, client
    tag = "sandbox:1"

    if tag not in client.images.list():
        try: 
            client.images.build(path=path, dockerfile=f"{path}/Dockerfile", tag=tag)
        except docker.errors.BuildError as e:
            logging.error(f"Error al construir la imagen: {e}")
            return None
        except Exception as e:
            logging.error(f"Error al construir la imagen: {e}")
            return None
            
    return tag

def create_container(image):
    global path, client
    try:
        volumes = {
            f'{path}/test': {
                'bind': '/data',
                'mode': 'rw'
            }
        }
        container = client.containers.run(image=image, name="sanbox_cont", volumes=volumes, command="sleep infinity", detach=True)
        logging.debug(f"Contenedor {container.id} iniciado exitosamente.")
    except Exception as e:
        logging.error(f"Error al iniciar el contenedor: {e}")
        return None
    
    return container

def run_code_in_container(container, language):
    """
    Finds and compiles code files within the container's /data volume.

    Args:
        container: The Docker container object.
        language: The programming language ('c' or 'python').

    Returns:
        A dictionary mapping filenames to their compilation results
        {filename: {'exit_code': int, 'output': str}} or None if an error occurs.
    """
    results = {}
    find_command = None
    file_extension = None

    # 1. Determine find command based on language
    if language == 'c':
        file_extension = "*.c"
    elif language == 'python':
        file_extension = "*.py"
    else:
        logging.error(f"Unsupported language: {language}")
        return None

    try:
        find_command = f"find /data -type f -name '{file_extension}'"
        logging.debug(f"Finding files with command: {find_command}")

        # 2. Execute find command to get the list of files
        exit_code_find, output_find = container.exec_run(cmd=find_command, user='sandboxuser')

        if exit_code_find != 0:
            # Find returning non-zero might mean no files found, which isn't necessarily an error
            if "No such file or directory" not in output_find.decode('utf-8', errors='ignore'):
                 logging.error(f"Failed to find files. Exit code: {exit_code_find}, Output: {output_find.decode('utf-8', errors='ignore')}")
            # Return empty results if find fails or finds nothing
            return results

        files_to_compile = output_find.decode('utf-8').strip().split('\n')
        if not files_to_compile or files_to_compile == ['']:
             logging.info(f"No .{language} files found in /data.")
             return results

        logging.debug(f"Files found: {files_to_compile}")

        # 3. Iterate and compile each file
        executables_to_clean = []
        for file_path in files_to_compile:
            if not file_path: continue # Skip empty lines if any

            filename = os.path.basename(file_path)
            compile_command = None
            exit_code = -1
            output = b''

            try:
                if language == 'c':
                    # Store executable in /sandbox to keep /data clean and avoid permission issues
                    executable_name = os.path.splitext(filename)[0]
                    executable_path = f"/sandbox/{executable_name}" # Use /sandbox for output
                    compile_command = f"gcc {file_path} -o {executable_path}"
                    logging.debug(f"Compiling C file: {compile_command}")
                    # Run compilation in /sandbox where user has write permissions
                    exit_code, output = container.exec_run(cmd=compile_command, user='sandboxuser', workdir='/sandbox')
                    if exit_code == 0:
                        executables_to_clean.append(executable_path) # Add for cleanup
                        logging.debug(f"C compilation successful for {filename}.")
                    else:
                        logging.warning(f"C compilation failed for {filename} (Exit Code: {exit_code}). Output:\n{output.decode('utf-8', errors='ignore')}")


                elif language == 'python':
                    compile_command = f"python3 -m py_compile {file_path}"
                    logging.debug(f"Checking Python syntax for: {compile_command}")
                    # Can run this from anywhere, /sandbox is fine
                    exit_code, output = container.exec_run(cmd=compile_command, user='sandboxuser', workdir='/sandbox')
                    if exit_code == 0:
                         logging.debug(f"Python syntax check successful for {filename}.")
                    else:
                         logging.warning(f"Python syntax check failed for {filename} (Exit Code: {exit_code}). Output:\n{output.decode('utf-8', errors='ignore')}")


                results[filename] = {
                    'exit_code': exit_code,
                    'output': output.decode('utf-8', errors='ignore').strip()
                }
                # Log output only if there is something interesting (error or warning)
                if exit_code != 0 or output:
                    logging.debug(f"Result for {filename}: Exit={exit_code}, Output=\n{results[filename]['output']}")

            except docker.errors.APIError as e_compile:
                 logging.error(f"Docker API error compiling {filename}: {e_compile}")
                 results[filename] = {'exit_code': -1, 'output': f"Docker API Error: {e_compile}"}
            except Exception as e_compile:
                 logging.error(f"Error compiling {filename}: {e_compile}")
                 results[filename] = {'exit_code': -1, 'output': f"Error: {e_compile}"}


    except docker.errors.APIError as e_find:
        logging.error(f"Docker API error finding files: {e_find}")
        return None # Critical error finding files
    except Exception as e_find:
        logging.error(f"Error finding files in container: {e_find}")
        return None # Critical error finding files
    finally:
        # 4. Clean up C executables from /sandbox
        if executables_to_clean:
            try:
                # Ensure executables_to_clean contains only valid paths before joining
                valid_paths = [p for p in executables_to_clean if p and p.startswith('/sandbox/')]
                if valid_paths:
                    cleanup_command = "rm -f " + " ".join(valid_paths)
                    logging.debug(f"Cleaning up executables: {cleanup_command}")
                    exit_code_rm, out_rm = container.exec_run(cmd=cleanup_command, user='sandboxuser', workdir='/sandbox')
                    if exit_code_rm == 0:
                        logging.debug("Successfully cleaned up C executables.")
                    else:
                        logging.warning(f"Failed to clean up C executables (Exit Code: {exit_code_rm}): {out_rm.decode('utf-8', errors='ignore')}")
                else:
                    logging.debug("No valid executable paths found for cleanup.")
            except Exception as e_clean:
                logging.warning(f"Error cleaning up executables: {e_clean}")

    return results

# client.images.build(tag="sandbox:1", path=path)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    tag = build_image()
    if not tag:
        logging.error("Failed to build image. Exiting.")
        exit(1)

    # Check if container exists and stop/remove it
    container_name = "sanbox_cont"
    try:
        cont = client.containers.get(container_name)
        logging.debug(f"Found existing container '{container_name}'")
    except docker.errors.NotFound:
        logging.debug(f"No existing container '{container_name}' found.")
    except Exception as e:
        logging.error(f"Error managing existing container: {e}")

    if cont == None:
        cont = create_container(tag)
        if cont == None:
            logging.error("Failed to create container. Exiting.")
            exit(1)

    logging.info("--- Compiling C code in /data ---")
    c_results = run_code_in_container(cont, "c")
    if c_results is not None:
        if not c_results:
            print("No C files found or processed in /data.")
        else:
            print("C Compilation Results:")
            for filename, result in c_results.items():
                print(f"  File: {filename}")
                print(f"    Exit Code: {result['exit_code']}")
                if result['output']:
                    print(f"    Output:\n      {result['output'].replace('\n', '\n      ')}") # Indent output
                else:
                    print("    Output: <None>")
                print("-" * 10)
    else:
        print("Error occurred during C compilation process.")

    # Stop and remove the container when done
    try:
        logging.debug(f"Stopping container {cont.id}...")
        cont.stop()
        logging.debug(f"Removing container {cont.id}...")
        cont.remove()
        logging.debug("Container stopped and removed.")
    except Exception as e:
        logging.error(f"Error stopping/removing container: {e}")