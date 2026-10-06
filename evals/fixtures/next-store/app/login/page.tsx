export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string; error?: string }> }) {
  const { next = '/account', error } = await searchParams;

  return (
    <form method="post" action="/api/login">
      <input type="hidden" name="next" value={next} />
      <label>
        Email <input name="email" type="email" required />
      </label>
      <label>
        Password <input name="password" type="password" required />
      </label>
      {error && <p role="alert">Invalid email or password</p>}
      <button type="submit">Sign in</button>
    </form>
  );
}
