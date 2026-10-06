import { FormEvent, useEffect, useState } from 'react';
import { getMyProfile, Profile, updateMyProfile } from '../api/profile';

export function EditProfilePage() {
  const [form, setForm] = useState<Profile | null>(null);

  useEffect(() => {
    getMyProfile().then(setForm);
  }, []);

  if (!form) return null;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (form) setForm(await updateMyProfile(form));
  }

  return (
    <form onSubmit={onSubmit}>
      <label>
        Display name
        <input value={form.displayName} onChange={(e) => setForm({ ...form, displayName: e.target.value })} />
      </label>
      <label>
        Website
        <input value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} />
      </label>
      <label>
        Bio (markdown)
        <textarea value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} />
      </label>
      <button type="submit">Save</button>
    </form>
  );
}
