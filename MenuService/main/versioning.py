from rest_framework.versioning import BaseVersioning

class BuildHeaderVersioning(BaseVersioning):
    default_version = 'current'
    legacy_threshold = 200

    def determine_version(self, request, *args, **kwargs):
        header = request.headers.get('X-App-Build') or request.headers.get('X-App-Version')
        try:
            build = int(header) if header is not None else None
        except ValueError:
            build = None
        if build is not None and build < self.legacy_threshold:
            return 'legacy'
        return 'current'