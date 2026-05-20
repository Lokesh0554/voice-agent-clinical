# Placeholder for persistent patient data (swap for Postgres/SQLAlchemy ORM in prod)

class PatientMemory:
    _store = dict()

    def get(self, patient_id):
        return self._store.get(patient_id, {})
    
    def set(self, patient_id, data):
        self._store[patient_id] = data