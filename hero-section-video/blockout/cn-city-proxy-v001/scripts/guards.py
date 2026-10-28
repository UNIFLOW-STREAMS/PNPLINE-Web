from pathlib import Path
import hashlib
def validate_paths(base, output, root, expected_sha):
    base,output,root=map(lambda p:Path(p).resolve(),(base,output,root))
    if base==output:raise ValueError('Input/output paths coincide')
    if not output.is_relative_to(root) or output.is_relative_to(root/'inputs'):
        raise ValueError('Output outside allowed artifact area')
    if output.exists():raise FileExistsError('Refusing to overwrite '+str(output))
    if hashlib.sha256(base.read_bytes()).hexdigest()!=expected_sha:
        raise ValueError('Source hash mismatch')
