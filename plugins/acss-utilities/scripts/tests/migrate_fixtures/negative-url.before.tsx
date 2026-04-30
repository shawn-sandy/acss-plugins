// Negative case: URL containing sm:foo must NOT be rewritten
const url = "https://example.com/sm:foo?bar=md:baz";
const link = <a href="https://cdn.example.com/sm:icon.svg">Link</a>;
// Only className values should be touched
const cls = <div className="sm:hide">x</div>;
